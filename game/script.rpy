define config.allow_skipping = False
define config.rollback_enabled = False

style default:
    hinting "bytecode"

define organes = get_references_organes()

# données courantes
# variables globales pour que les actions y aient accès
default organe = "AN"
default ordre_du_jour = None # dict[tuple[str, str], str] # (bibard, suffixe) -> titre
default bibard = None
default bibard_suffixe = None
default titre_texte = None
default amdts_par_division = None # dict[str, list[amdt]] # divisions triées, amendements aussi
default nbr_amdts_restants = None
default amendement = None

label main_menu:
return

label start:
call screen main_eliasse
return

screen main_eliasse():
    # options d'affichage
    default show_cosignataires = False
    default show_derouleur = True
    default show_texte = True
    default show_text_selection = False

    default suivi_auto = True # visible sur l'interface vanilla
    default refresh = True    # couper l'utilisation d'internet, en gros (en faire un persistent ?)

    python: # actualisation régulière
        if amendement:
            division = amendement["placeReference"]
        elif amdts_par_division:
            division = next(iter(amdts_par_division))
        else:
            division = None

    # timer 1 action ActuateProchain() refresh refresh

    # division titre/reste/bottom
    side "t c b":

        # barre de titre
        frame:
            style "gradientedframe"

            fixed:
                yfit True

                # en attendant la syntaxe f-string
                $ nom_organe = organes[organe]
                text "[nom_organe]":
                    xalign .0

                text "[titre_texte]":
                    xalign .5

                hbox:
                    xalign 1.

                    text "([bibard][bibard_suffixe])"

                    textbutton "Texte de référence":
                        action ToggleScreenVariable("show_texte")

                    textbutton "Dérouleur":
                        action ToggleScreenVariable("show_derouleur")

        side "c r":

            side "c b":

                frame:
                    background "#fff"
                    padding (0, 10)

                    side "l c r":

                        # bouton gauche
                        textbutton "⬅️":
                            text_size 50
                            yalign .5
                            action NullAction() # TODO

                        # texte et présentation de l'amendement
                        add "#e6e3e3" # TODO

                        # bouton droit
                        textbutton "➡️":
                            text_size 50
                            yalign .5
                            action NullAction() # TODO

                # texte sur lequel l'amendement porte
                if show_texte:
                    viewport:
                        scrollbars "vertical"
                        ysize 200
                        vscrollbar_unscrollable "hide"

                        add "#e6e3e3"
                        text "[[texte]" # TODO
                else:
                    null

            # dérouleur
            if show_derouleur:
                frame:
                    style "default"
                    background "#ffb"
                    xsize 500
                    yfill True

                    vbox:
                        frame:
                            style "gradientedframe"
                            xfill False

                            fixed:
                                yfit True

                                # sélecteur de division # TODO

                                text "Dérouleur prévisionnel":
                                    xalign .5

                                # fermer le dérouleur (pas vraiment nécessaire, il y a le bouton juste au-dessus)

                        frame:
                            style "gradientedframe"
                            xfill True

                            text "[division]":
                                xalign .5

                        viewport:
                            scrollbars "vertical"
                            vscrollbar_unscrollable "hide"

                            null # TODO
                            # for amdt in ():
                            #     textbutton "[[amdt]":
                            #         action SetVariable("amdt_id", amdt.id)
            else:
                null

        # footer
        frame:
            style "gradientedframe"
            fixed:
                yfill False
                yfit True

                if suivi_auto:
                    textbutton "Suivi auto activé, [nbr_amdts_restants] amendements restants":
                        xalign .0
                        action SetScreenVariable("suivi_auto", False)

                else:
                    textbutton "Amendement en cours de discussion":
                        xalign .0
                        action SetScreenVariable("suivi_auto", True)

                textbutton "Changer de texte":
                    xalign .5
                    action SetScreenVariable("show_text_selection", True)

                textbutton "Cosignataires":
                    xalign 1.
                    action SetScreenVariable("show_cosignataires", True)

    if show_text_selection:
        default local_organe = organe

        dismiss action SetScreenVariable("show_text_selection", False)

        frame:
            xsize 1000
            yfill False
            align (.5, .5)
            modal True

            vbox:
                frame:
                    style "gradientedframe"
                    xfill True

                    text "Sélection du texte":
                        xalign .5

                hbox:
                    fixed:
                        yfit True
                        xsize 200

                        text "Organe"

                    # en attendant la syntaxe f-string
                    $ nom_organe = organes[local_organe]
                    textbutton "[nom_organe]":
                        xfill True
                        text_size 25
                        action CaptureFocus("organes_drop")

                hbox:
                    fixed:
                        yfit True
                        xsize 200

                        text "Texte"

                    textbutton "[titre_texte]":
                        xfill True
                        text_size 25
                        action CaptureFocus("textes_drop")

    if GetFocusRect("organes_drop"):
        dismiss action ClearFocus("organes_drop")

        nearrect:
            focus "organes_drop"

            frame:
                modal True
                style "dropdownframe"
                has vbox

                for organe_id, organe_name in organes.items():
                    textbutton "[organe_name]":
                        text_size 25
                        if organe_id != local_organe:
                            action [SetScreenVariable("local_organe", organe_id), ClearFocus("organes_drop")]

    if GetFocusRect("textes_drop"):
        dismiss action ClearFocus("textes_drop")

        nearrect:
            focus "textes_drop"

            frame:
                modal True
                style "dropdownframe"
                has vbox

                for odj_el in get_textes_ordre_du_jour(local_organe):
                    textbutton "[odj_el[textTitre]]":
                        text_size 25
                        if odj_el["textBibard"] != bibard:
                            action NullAction()

    if show_cosignataires:
        dismiss action SetScreenVariable("show_cosignataires", False)

        frame:
            xfill False
            yfill False
            align (.5, .5)

            text "(cosignataires)" # TODO

style gradientedframe is default:
    background vgradient("#77f", "#00f")

style dropdownframe is default:
    background Frame(
        Fixed(
            Solid("#000", xysize=(10, 10)),
            Solid("#fff", xysize=(8, 8), align=(.5, .5)),
            fit_first=True),
        4, 4)
    padding (4, 4)

init python:
    @renpy.pure
    class SetOrgane(Action):
        def __init__(self, organe):
            self.organe = organe

        def __call__(self):
            store.organe = self.organe
            renpy.run(ActuateOrdreDuJour())

            store.bibard = store.bibard_suffixe = store.titre_texte = store.amdts_par_division = store.amendement = None

        def get_sensitive(self):
            return (organe != self.organe) and (organe in organes)

        def get_selected(self):
            return organe == self.organe

    class ActuateOrdreDuJour(Action):
        """
        Actualise l'ordre du jour sans réinitialiser les données liées
        au texte et à l'amendement courants.
        """
        def __call__(self):
            store.ordre_du_jour = get_ordre_du_jour(organe)

    class ActuateProchain(Action):
        """
        Fait toute l'actualisation du prochain texte et amendement à discuter pour l'organe courant.
        """
        def __call__(self):
            prochain_data = get_prochain_a_discuter(organe)
            prochain_bibard = prochain_data["bibard"]
            prochain_suffixe = prochain_data["bibardSuffixe"]
            prochain_amdt_num = prochain_data["numAmdt"]

            if (not ordre_du_jour) or ((prochain_bibard, prochain_suffixe) not in ordre_du_jour):
                renpy.run(ActuateOrdreDuJour())

            actuated = False # pour ne pas run ActuateAmdts deux fois

            text_action = SetText(prochain_bibard, prochain_suffixe)
            if renpy.is_sensitive(text_action):
                renpy.run(text_action)
                actuated = True

            if (amendement is None) or (amendement["numero"] != prochain_amdt_num):
                if not actuated:
                    renpy.run(ActuateAmdts())
                renpy.run(SetAmendement(prochain_amdt_num))

    @renpy.pure
    class SetText(Action):
        def __init__(self, bibard, suffixe=""):
            self.bibard = bibard
            self.suffixe = suffixe

        def __call__(self):
            store.bibard = self.bibard
            store.bibard_suffixe = self.suffixe
            store.titre_texte = ordre_du_jour[bibard, bibard_suffixe]
            renpy.run(ActuateAmdts())

            store.amendement = None

        def get_sensitive(self):
            return ((bibard != self.bibard) or (bibard_suffixe != self.suffixe))\
                and ordre_du_jour and ((self.bibard, self.suffixe) in ordre_du_jour)

        def get_selected(self):
            return (bibard == self.bibard) and (bibard_suffixe == self.suffixe)

    class ActuateAmdts(Action):
        """
        Actualise certaines données liées aux amendements liés au texte courant :
        amdts_par_division et nbr_amdts_restants.
        """
        def __call__(self):
            discussion = get_discussion(
                bibard=bibard,
                bibard_suffixe=bibard_suffixe,
                organe_abrv=organe,
            )

            store.nbr_amdts_restants = discussion["nbrAmdtRestant"]

            # liste de dicts
            divisions_raw = discussion["divisions"]
            # liste de "place" des divisions triées par "position"
            divisions = [d["place"] for d in sorted(divisions_raw, key=lambda d: d["position"])]

            # garantir l'ordre des divisions, puis modification par effet de bord
            # dict[str, list[amdt]] # divisions triées, amendements aussi
            store.amdts_par_division = amdts_par_division = {d : [] for d in divisions}
            for amdt in discussion["amendements"]:
                amdts_par_division[amdt["place"]].append(amdt)
            for dn, amdts in amdts_par_division.items():
                amdts.sort(key=lambda a: a["position"])

        def get_sensitive(self):
            return bibard is not None

    @renpy.pure
    class SetDivision(Action):
        """
        En réalité, change l'amendement, comme SetAmendement.
        """
        def __init__(self, div):
            self.div = div

        def __call__(self):
            if not self.get_selected():
                store.amendement = get_amendement(
                    store.amdts_par_division[self.div][0]["numero"],
                    bibard=bibard,
                    bibard_suffixe=bibard_suffixe,
                    organe_abrv=organe,
                )

        def get_sensitive(self):
            return (bibard is not None) and amdts_par_division and (self.div in amdts_par_division) # and ((amendement is None) or (amendement["place"] != self.div))

        def get_selected(self):
            return (amendement is not None) and (amendement["place"] == self.div)

    @renpy.pure
    class SetAmendement(Action):
        def __init__(self, amdt):
            self.amdt_num = amdt

        def __call__(self):
            store.amendement = get_amendement(
                self.amdt_num,
                bibard=bibard,
                bibard_suffixe=bibard_suffixe,
                organe_abrv=organe,
            )

        def get_sensitive(self):
            return ((amendement is None) or (amendement["numeroReference"] != self.amdt_num))

        def get_selected(self):
            return (amendement is not None) and (amendement["numeroReference"] == self.amdt_num)

    class ActuateAmendement(Action):
        def __call__(self):
            store.amendement = get_amendement(
                amendement["numeroReference"],
                bibard=bibard,
                bibard_suffixe=bibard_suffixe,
                organe_abrv=organe,
            )

        def get_sensitive(self):
            return (bibard is not None) and (amendement is not None)
