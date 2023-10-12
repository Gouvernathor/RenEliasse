import renpy # type: ignore

"""renpy
init python:
"""
import html
import re
import xml.etree.ElementTree as ET

# import lxml
# import lxml.html
import requests

# URLs disponibles :
# checkConnection.do
# prochainADiscuter.do           # done
# getParametresStatiques.do
# getVersionLivrable.do
# amdtDerouleur.do
# discussion.do
# amendement.do                  # done
# setTexteCookie.do
# discussionTache.do
# getListeReferenceDesOrganes.do
# textesOrdreDuJour.do           # done
# setOrganeCookie.do
# loadTextContentByBibard.do     # done

def get_prochain_a_discuter(organe="AN"):
    """
    Renvoie un dict json concernant le texte actuellement discuté
    ou prochain à être discuté.

    Clés :
    "bibard"
        identifiant du texte (str)
    "bibardSuffixe"
        suffixe à l'identifiant du texte (str)
    "legislature"
        numéro de la législature (str)
    "numAmdt"
        numéro/identifiant de l'amendement actuel / prochain (str)
    "organeAbrv"
        identifiant de l'instance (str)
    """
    data = requests.get(
        "http://eliasse.assemblee-nationale.fr/eliasse/prochainADiscuter.do",
        cookies=dict(FOCUSED_ORGANE=organe),
    ).json()
    prochain_data = data.pop("prochainADiscuter")
    assert not data

    # à tester, des fois ça renvoie celui de l'AN quand on demande une commission...
    if prochain_data["organeAbrv"] != organe:
        return None

    return prochain_data

def get_textes_ordre_du_jour(organe="AN"):
    """
    Renvoie une liste d'éléments d'ordre du jour.
    Chaque élément est un dict json.

    Clés des éléments :
    "textBibard"
        identifiant du texte (str)
    "textBibardSuffixe"
        suffixe à l'identifiant du texte (str)
    "textTitre"
        titre du texte (str)
    """
    data = requests.get(
        "http://eliasse.assemblee-nationale.fr/eliasse/textesOrdreDuJour.do",
        params=dict(
            organeAbrv=organe,
        ),
    ).json()

    return data

def get_amendement(num_amdt, bibard, *, bibard_suffixe="", organe_abrv="AN", legislature=16):
    data = requests.get(
        "http://eliasse.assemblee-nationale.fr/eliasse/amendement.do",
        params=dict(
            legislature=legislature,
            bibard=bibard,
            bibardSuffixe=bibard_suffixe,
            organeAbrv=organe_abrv,
            numAmdt=num_amdt,
        ),
    ).json()
    amendement, = data.pop("amendements")
    assert not data
    return amendement

def get_2_textes_de_reference(amendement):
    """
    Renvoie un tuple de deux éléments,
    le premier est l'article (en général) de référence,
    le second est l'amendement sous-amendé.

    Pour les amendements qui créent des articles, sans
    texte de référence, ou pour leurs sous-amendements,
    le premier élément est None.
    Quand ce n'est pas un sous-amendement qu'on considère,
    le second élément est None.
    """

    article = None
    main_amdt = None

    # tiré du JS
    is_on_article_additionnel = amendement["division"]["avantApres"] != "A"
    is_sous_amendement = amendement.get("numeroParent", None) != "X"

    if not is_on_article_additionnel:
        article = get_article_de_reference(amendement)

    if False and is_sous_amendement: # fonctionne pas for some reason
        main_amdt = get_main_amendement(amendement)

    return article, main_amdt

def get_article_de_reference(amendement):
    return requests.get(
        "http://eliasse.assemblee-nationale.fr/eliasse/loadTextContentByBibard.do",
        params=dict(
            bibard=amendement["bibard"],
            bibardSuffixe=amendement["bibardSuffixe"],
            legislature=amendement["legislature"],
            isSousAmdt=False,
            ancreDivision=amendement["ancreDivisionTexteVise"],
        ),
    ).text

# requests.get(
#     "http://eliasse.assemblee-nationale.fr/eliasse/loadTextContentByBibard.do",
#     params=dict(
#         bibard=1674,
#         bibardSuffixe="",
#         legislature=16,
#         isSousAmdt=False,
#         ancreDivision="D_Article_7",
#     )
# ).text

def get_main_amendement(amendement):
    return requests.get(
        "http://eliasse.assemblee-nationale.fr/eliasse/loadTextContentByBibard.do",
        params=dict(
            bibard=amendement["bibard"],
            bibardSuffixe=amendement["bibardSuffixe"],
            legislature=amendement["legislature"],
            isSousAmdt=True,
            focusedOrgane=amendement["organeAbrv"],
            numeroParent=amendement["numeroParent"],
        ),
    ).text

# requests.get(
#     "http://eliasse.assemblee-nationale.fr/eliasse/loadTextContentByBibard.do",
#     params=dict(
#         bibard=1674,
#         bibardSuffixe="",
#         legislature=16,
#         isSousAmdt=True,
#         focusedOrgane="AN",
#         numeroParent="1121 (Rect)",
#     )
# ).text

def detricote_html(page):
    if isinstance(page, (str, bytes)):
        s = page
        # passer par fromstring (qui retire les commentaires au passage)
        # page = lxml.html.fromstring(s, lxml.html.HTMLParser(recover=True))
        # page = ET.fromstring(re.sub(r"<\?[^?]*\?>", "", s))
        s = html.unescape(s)
        try:
            page = ET.fromstring(s)
        except ET.ParseError:
            page = ET.fromstring(f"<div>{s}</div>")

    buf = []

    def parse_element(element):
        # retirer les blocs meta
        # pour les amendements en tout cas, on ne traite pas spécialement les <title>
        # parcourir les blocs p et span
            # pour chaque bloc p, ajouter \n
            # pour chaque bloc span, ajouter le contenu texte

        print(element.tag)
        buf.append(element.text or "")

        for subelement in element:
            if subelement.tag == "meta":
                continue

            parse_element(subelement)

        if element.tag == "p":
            buf.append("\n")

        buf.append(element.tail or "")

    parse_element(page)

    print(buf)
    return "".join(buf).strip()
