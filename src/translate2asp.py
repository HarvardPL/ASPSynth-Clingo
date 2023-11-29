#!/usr/bin/env python3

# Copyright 2023 President and Fellows of Harvard College
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Translates a ProSynth synthesis problem into an ASP program. When parsing the
# Souffle program containing candidate rules, it assumes that each candidate
# rule has been written on a single line. 

import os.path
import re

def uncap(s):
    return s[0].lower() + s[1:]


def translate_term(term, unquoted_symbols=False):
    if term.isnumeric() or term[0] == '"':
        return term
    if unquoted_symbols:
        return f'"{term}"'
    return term[0].upper() + term[1:]


def translate_atom(tokens, pos):
    pred = tokens[pos]
    pos += 1
    assert(tokens[pos] == "(")
    pos += 1
    out_atom = [uncap(pred), "("]
    while tokens[pos] != ")":
        out_atom.extend(translate_term(tokens[pos]))
        pos += 1
        if tokens[pos] == ",":
            out_atom.append(", ")
            pos += 1
    out_atom.append(")")
    pos += 1
    return ("".join(out_atom), pos)


def translate_rule(in_rule):
    tokens = [t for t in re.split(r"\s+|(,|:-|\)|\()", in_rule) if t]
    (head, pos) = translate_atom(tokens, 0)
    assert(tokens[pos] == ":-")
    out_rule = [head, " :- "]
    pos += 1
    cnt = 0
    p = re.compile(r"rule\((.*)\)")
    rule_id = None
    while tokens[pos] != ".":
        (pred, pos) = translate_atom(tokens, pos)
        m = p.fullmatch(pred)
        if m:
            rule_id = m.group(1)
        cnt += 1
        out_rule.append(pred)
        if tokens[pos] == ",":
            out_rule.append(", ")
            pos += 1
    out_rule.append(".")
    return ("".join(out_rule), cnt - 1, rule_id)


rel_decl_pat = re.compile(r".decl\s+([a-zA-Z0-9:_]+)\((.*)\)")


def translate_rules(rule_file, minimize, acc):
    rule_ids = []
    rule_sizes = []
    arities = {}
    with open(rule_file, "r") as f:
        cnt = 0
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line[0] == ".":
                m = rel_decl_pat.match(line)
                if m:
                    arities[uncap(m.group(1))] = len(m.group(2).split(","))
                continue
            (rule, size, rule_id) = translate_rule(line)
            if rule_id != None:
                rule_ids.append(rule_id)
            acc.append(rule)
            rule_sizes.append(size)
            if minimize == "rules":
                acc.append("rule_weight(%d, 1)." % cnt)
            elif minimize == "premises":
                acc.append("rule_weight(%d, %d)." % (cnt, size))
            cnt += 1
    return (rule_sizes, arities, rule_ids)


def translate_facts(fact_file, acc):
    base = os.path.basename(fact_file)
    name = os.path.splitext(base)[0]
    if name == "Rule": return
    name = name[0].lower() + name[1:]
    with open(fact_file, "r") as f:
        for line in f:
            out_line = [name, "("]
            line = line.strip()
            args = []
            for arg in line.split("\t"):
                args.append(translate_term(arg, unquoted_symbols=True))
            out_line.append(", ".join(args))
            out_line.append(").")
            acc.append("".join(out_line))


def translate_spec_file(spec_file, name, expected, acc):
    with open(spec_file, "r") as f:
        for line in f:
            args = []
            for arg in line.strip().split("\t"):
                args.append(translate_term(arg, unquoted_symbols=True))
            args = ", ".join(args)
            out_line = [name, "__POS(" if expected else "__NEG(", args, ")."]
            acc.append("".join(out_line))


def translate_spec(spec_base, arities, acc):
    raw_name = os.path.basename(spec_base)
    name = uncap(raw_name)
    if not name in arities:
        raise Exception(f"Unrecognized relation: {raw_name}")
    args = ", ".join("X" + str(i) for i in range(arities[name]))
    pred = f"{name}({args})"
    pos = f"{name}__POS({args})"
    neg = f"{name}__NEG({args})"
    pos_file = spec_base + ".expected"
    translate_spec_file(pos_file, name, True, acc)
    acc.append(f":- {pos}, not {pred}.")
    neg_file = spec_base + ".undesired"
    if os.path.exists(neg_file):
        translate_spec_file(neg_file, name, False, acc)
        acc.append(f":- {neg}, {pred}.")
    else:
        acc.append(f":- {pred}, not {pos}.")


def translate(bm_dir, minimize):
    acc = []
    for f in os.listdir(bm_dir):
        if f.endswith(".facts"):
            translate_facts(os.path.join(bm_dir, f), acc)
    rule_file = os.path.join(bm_dir, "rules.small.dl")
    (rule_sizes, arities, rule_ids) = translate_rules(rule_file, minimize, acc)

    for f in os.listdir(bm_dir):
        if f.endswith(".expected"):
            f = os.path.join(bm_dir, f)
            f = os.path.splitext(f)[0]
            translate_spec(f, arities, acc)

    for rule_id in rule_ids:
        acc.append(f"{{ rule({rule_id}) }}.")
    acc.append("#show rule/1.")
    if minimize != "none":
        acc.append(":~ rule(X), rule_weight(X, W). [W, X]")

    print("*** Rule sizes ***")
    for (i, sz) in enumerate(rule_sizes):
        print("rule(%d) has %d premises" % (i, sz))
    return acc
