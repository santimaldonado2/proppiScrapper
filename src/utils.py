import re


def get_formated_telephone(telephone):
    if not telephone:
        return ""

    telephone = re.sub('[^0-9/]', '', telephone)

    if telephone.startswith('0'):
        telephone = telephone[1:]

    if telephone.startswith("35115"):
        telephone = "351" + telephone[5:]
    elif telephone.startswith("15"):
        telephone = "351" + telephone[2:]

    telephones = telephone.split("/")

    return telephones[0]
