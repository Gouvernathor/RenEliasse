define config.allow_skipping = False
define config.rollback_enabled = False

label main_menu:
return

label start:
call screen main_eliasse
return

screen main_eliasse():
    default show_cosignataires = False
    default show_derouleur = True
    default show_texte = True
    default show_text_selection = False
    default refresh = False

    # division titre/reste/bottom
    side "t c b":

        # barre de titre
        frame:
            style "gradientedframe"

            fixed:
                yfit True

                text "[[organe]":
                    xalign .0

                text "[[titre_texte]":
                    xalign .5

                hbox:
                    xalign 1.

                    # text "(3546 (?))"

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

                        # texte et présentation de l'amendement
                        add "#e6e3e3"

                        # bouton droit
                        textbutton "➡️":
                            text_size 50
                            yalign .5

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
                add Solid("#ffb", xsize=100)

        # footer
        frame:
            style "gradientedframe"
            fixed:
                yfill False
                yfit True

                if refresh:
                    textbutton "Suivi auto activé, [[amdts] adts restants":
                        xalign .0
                        action SetScreenVariable("refresh", False)

                else:
                    textbutton "Amendement en cours de discussion":
                        xalign .0
                        action SetScreenVariable("refresh", True)

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
