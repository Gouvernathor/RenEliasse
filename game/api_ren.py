import renpy # type: ignore

"""renpy
init python:
"""
import html
import re
import xml.etree.ElementTree as ET

import requests

# URLs disponibles :
# checkConnection.do
# prochainADiscuter.do           # done
# getParametresStatiques.do
# getVersionLivrable.do
# amdtDerouleur.do               # inutile avec discussion.do (mêmes params, renvoie l'élément "amendements")
# discussion.do                  # done
# amendement.do                  # done
# setTexteCookie.do
# discussionTache.do
# getListeReferenceDesOrganes.do # done
# textesOrdreDuJour.do           # done
# setOrganeCookie.do
# loadTextContentByBibard.do     # done

def get_references_organes():
    """
    Renvoie un dictionnaire {identifiant (str) : nom (str)}.
    """
    data = requests.get(
        "http://eliasse.assemblee-nationale.fr/eliasse/getListeReferenceDesOrganes.do",
    ).json()

    return {d["value"]: d["text"] for d in data}

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
    # session = requests.Session()
    # session.get(
    #     "http://eliasse.assemblee-nationale.fr/eliasse/setOrganeCookie.do",
    #     params=dict(
    #         selectedOrgane=organe,
    #         checkOrgane=True,
    #     )
    # )
    # en fait inutile, c'est juste qu'il faut avoir le bon cookie ET le bon paramètre

    data = requests.get(
        "http://eliasse.assemblee-nationale.fr/eliasse/prochainADiscuter.do",
        cookies=dict(FOSUSED_ORGANE=organe),
        params=dict(
            organeAbrv=organe,
        ),
    ).json()
    prochain_data = data.pop("prochainADiscuter")
    assert not data
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

def get_ordre_du_jour(organe="AN"):
    """
    Renvoie un dictionnaire {(bibard, suffixe): titre}
    """
    return {(o["textBibard"], o["textBibardSuffixe"]): o["textTitre"] for o in get_textes_ordre_du_jour(organe)}

def get_discussion(bibard, *, bibard_suffixe="", organe_abrv="AN", legislature=16):
    """
    Renvoie un dict avec des clés diverses.

    (non exhaustif)
    "amendements"
        une liste de dicts d'amendement, avec les clés suivantes (non exhaustif) :
        "alineaLabel"
            semble donner des infos sur l'alinea concerné,
            avec S pour les amendements de suppression,
            "" pour les articles additionnels ou le titre...
        "auteurGroupe"
            abbréviation du groupe de l'auteur (lourd potentiel)
        "auteurLabel"
            nom de l'auteur, prêt à l'affichage dans la liste dérouleur
        "discussionCommune"
            identifiant de discussion commune, ou ""
        "discussionIdentique"
            identifiant de groupe d'amendements identiques, ou ""
        "numero"
            numéro officiel de l'amendement
        "parentNumero"
            (probablement) pour les sous-amendements, numéro officiel du parent
        "place"
            identifiant de division, voir plus loin
            propre à l'affichage *et* unique, apparemment
        "position"
            clé de tri des amendements (à la fois en int et en alphabétique)
        "sort"
            sort en toutes lettres en séance, ou "" avant (et pendant) l'exament de l'amendement
    "divisions"
        liste d'endroits où des amendements peuvent être placés
        deux clés utiles (la troisième est null) :
        "place"
            identifiant lisible qu'on retrouve dans les amendements, plus haut
        "position"
            clé de tri des divisions (à la fois en int et en alphabétique)
    "nbrAmdtRestant"
        nombre d'amendements restants, str à passer par int
    "type"
        type de texte, comme "projet de loi" ou "proposition de loi"
    "bibard"
    "bibardSuffixe"
    "legislature"
    "organe"
    "titre"
        relatifs au texte
    """
    data, = requests.get(
        "http://eliasse.assemblee-nationale.fr/eliasse/discussion.do",
        params=dict(
            bibard=bibard,
            bibardSuffixe=bibard_suffixe,
            organeAbrv=organe_abrv,
            legislature=legislature,
        ),
    ).json().values()
    return data

def get_amendement(num_amdt, bibard, *, bibard_suffixe="", organe_abrv="AN", legislature=16):
    """
    Renvoie un dict assez énorme, avec beaucoup de clés.

    (non exhaustif)
    "placeReference"
        identifiant de division, voir get_discussion
    "ancreDivisionTexteVise"
        autre identifiant de la même division, pour le texte de référence
    "place"
        le même emplacement, écrit en HTML
    "division"
        un dict avec quelques clés toutes moins utiles que placeReference
    "dispositif"
        le texte de l'amendement proprement dit, en HTML
    "exposeSommaire"
        l'exposé sommaire, en HTML
    "auteur"
        diverses infos sur l'auteur (non exhaustif) :
        "auteurLabel"
            nom de l'auteur prêt à afficher
        "qualite"
            (probablement) généralement None, mais contient des choses pour le rapporteur et le gouvernement
        "estGouvernement"
            (probablement) un flag, "0" si non (donc on doit passer par int()...)
        "estRapporteur"
            (probablement) idem
    "cosignataires"
        liste de dicts semblables à "auteur", sauf que estGouvernement et estRapporteur sont toujours ""
    "listeDesSignataires"
        string rassemblant tous les signataires, prêt à afficher
    "sortEnSeance"
        comme "sort" pour get_discussion
    "numeroParent"
        (probablement) comme "parentNumero" pour get_discussion
    "numero"
    "numeroLong"
    "numeroReference"
        numero est strictement numérique (mais toujours un str)
        Long peut contenir le " (Rect)"
        en commission, numeroReference commence par une ou des lettres
        en séance, numeroReference est égal à numero
    "position"
        comme dans get_discussion
    "bibard"
    "bibardSuffixe"
    "legislature"
    "organeAbrv"
        relatifs au texte
    "texte"
        d'autres infos relatives au texte, dans un dict :
        "numBibard"
        "numeroLegislature"
            toujours pareil
        "titre"
        "titreCourt"
            les deux sont en fullcaps
    """
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
