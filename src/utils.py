import re


def get_formated(telephone):
    if not telephone:
        return ""

    telephone = re.sub('[^1-9/]', '', telephone)

    if telephone[0:1] == '0':
        telephone = telephone[1:]

    if telephone.startswith("35115"):
        telephone = "351" + telephone[5:]

    telephone = telephone.split("/")

    return telephone[0]
