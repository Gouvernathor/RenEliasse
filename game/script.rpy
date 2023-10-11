define config.rollback_enabled = False

label main_menu:
return

label start:
call screen main_eliasse
return

screen main_eliasse():
    default show_texte = True
    default show_derouleur = True
    default refresh = False

    # division titre/reste/bottom
    side "t c b":

        # barre de titre
        fixed:
            yfill False
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

                add "#009"

                if show_texte:
                    add Solid("#090", ysize=100)
                else:
                    null

            if show_derouleur:
                add Solid("#900", xsize=100)
            else:
                null

        # footer
        fixed:
            yfill False
            yfit True

            if refresh:
                text "Suivi auto activé, [[amdts] adts restants":
                    xalign .0
            else:
                textbutton "Amendement en cours de discussion":
                    xalign .0
                    action SetScreenVariable("refresh", True)

            textbutton "Changer de texte":
                xalign .5
                action NullAction()
                # action Show("text_selection") # needs to be modal

            textbutton "Cosignataires":
                xalign 1.
                action NullAction()
