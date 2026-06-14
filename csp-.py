import sys
import time

class Match:
    def __init__(self, idx: int, team1: str, team2: str):
        self.idx = idx
        self.team1 = team1
        self.team2 = team2
        self.teams = frozenset([team1, team2])

    def __repr__(self):
        return f"Match({self.team1} vs {self.team2})"

def parse_input(lines: list):
    idx = 0

    S = int(lines[idx]); idx += 1
    stadiums = lines[idx].split(); idx += 1
    D = int(lines[idx]); idx += 1
    H = int(lines[idx]); idx += 1
    N = int(lines[idx]); idx += 1

    matches = []
    for i in range(N):
        parts = lines[idx].split(); idx += 1
        matches.append(Match(i, parts[0], parts[1]))

    K = int(lines[idx]); idx += 1
    sensitive_pairs = []
    for _ in range(K):
        parts = lines[idx].split(); idx += 1
        sensitive_pairs.append(frozenset([parts[0], parts[1]]))

    return S, stadiums, D, H, N, matches, K, sensitive_pairs

def build_domains(matches: list, D: int, H: int, stadiums: list):
    full_domain = [
        (d, h, st)
        for d in range(1, D + 1)
        for h in range(1, H + 1)
        for st in stadiums
    ]
    return {m.idx: list(full_domain) for m in matches}


def build_neighbors(matches: list, sensitive_set: set):
  
    neighbors = {m.idx: set() for m in matches}
    n = len(matches)
    for i in range(n):
        for j in range(i + 1, n):
            mi, mj = matches[i], matches[j]
            neighbors[mi.idx].add(mj.idx)
            neighbors[mj.idx].add(mi.idx)
    return neighbors


def shares_team(m1: Match, m2: Match) -> bool:
    return bool(m1.teams & m2.teams)


def is_consistent(match: Match, value, assignment: dict,
                  match_map: dict, sensitive_set: set) -> bool:
    day, hour, stadium = value
    for assigned_idx, assigned_val in assignment.items():
        other = match_map[assigned_idx]
        a_day, a_hour, a_stadium = assigned_val

        if (a_day, a_hour, a_stadium) == (day, hour, stadium):
            return False

        if shares_team(match, other) and a_day == day:
            return False

        if (match.idx in sensitive_set and assigned_idx in sensitive_set
                and a_day == day):
            return False

    return True



def forward_check(match: Match, value, assignment: dict,
                  domains: dict, match_map: dict, sensitive_set: set):
   
    day, hour, stadium = value
    pruned = {}

    for var_idx, domain in domains.items():
        if var_idx in assignment:
            continue

        other = match_map[var_idx]
        to_remove = []

        for val in domain:
            v_day, v_hour, v_stadium = val

            if (v_day, v_hour, v_stadium) == (day, hour, stadium):
                to_remove.append(val)
                continue

            if shares_team(match, other) and v_day == day:
                to_remove.append(val)
                continue

            if (match.idx in sensitive_set and var_idx in sensitive_set
                    and v_day == day):
                to_remove.append(val)
                continue

        if to_remove:
            pruned[var_idx] = to_remove
            for val in to_remove:
                domain.remove(val)

            if not domain:
                return None

    return pruned

