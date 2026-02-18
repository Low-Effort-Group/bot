admins = [
    954817064718200962, 
    974598822229598238,
    550938387796983819,
    225622023982809088,
]


def check_perm(uid):
    for admin in admins:
        if uid == admin:
            return True
    return False
