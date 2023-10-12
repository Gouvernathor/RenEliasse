define config.allow_skipping = False
define config.rollback_enabled = False

define organes = get_references_organes()

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

    # données courantes
    default organe = "AN"
    default bibard = None
    default amdt_id = None
    default amdts_par_art = None # dict[str, list]

    # timer 1 action NullAction() refresh refresh

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

                text "[[titre_texte]":
                    xalign .5

                hbox:
                    xalign 1.

                    text "[[bibard]"

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
                            action NullAction()

                        # texte et présentation de l'amendement
                        add "#e6e3e3"

                        # bouton droit
                        textbutton "➡️":
                            text_size 50
                            yalign .5
                            action NullAction()

                # texte sur lequel l'amendement porte
                showif show_texte:
                    viewport:
                        scrollbars "vertical"
                        ysize 200
                        vscrollbar_unscrollable "hide"

                        add "#e6e3e3"
                        text "[[texte]"

            # dérouleur
            showif show_derouleur:
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

                                # sélecteur d'article

                                text "Dérouleur prévisionnel":
                                    xalign .5

                                # fermer le dérouleur

                        frame:
                            style "gradientedframe"
                            xfill True

                            text "[[article X]":
                                xalign .5

                        viewport:
                            scrollbars "vertical"
                            vscrollbar_unscrollable "hide"

                            null
                            # for amdt in ():
                            #     textbutton "[[amdt]":
                            #         action SetScreenVariable("amdt_id", amdt.id)

        # footer
        frame:
            style "gradientedframe"
            fixed:
                yfill False
                yfit True

                if suivi_auto:
                    textbutton "Suivi auto activé, [[amdts] adts restants":
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
        dismiss action SetScreenVariable("show_text_selection", False)

        frame:
            xfill False
            yfill False
            align (.5, .5)

            text "(sélection du texte)"

    if show_cosignataires:
        dismiss action SetScreenVariable("show_cosignataires", False)

        frame:
            xfill False
            yfill False
            align (.5, .5)

            text "(cosignataires)"

style gradientedframe is default:
    background vgradient("#77f", "#00f")
