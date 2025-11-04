import pygame
import random
import sys
import os

# === CONFIG === #
LATO_CASELLA = 60
MARGINE = 4
DIM_GRIGLIA = 8
AREA_BLOCCHI_ALTEZZA = 320
FPS = 60

# === COLORI === #
NERO = (25, 25, 25)
GRIGIO = (55, 55, 55)
GRIGIO_SCURO = (35, 35, 35)
BIANCO = (235, 235, 235)
GIALLO = (255, 255, 100)
ROSSO = (255, 80, 80)
GHOST = (200, 200, 200, 120)  #trasparente
COLORI_BLOCCHI = [
    (255, 99, 71), (255, 165, 0), (255, 215, 0),
    (0, 255, 127), (0, 191, 255), (138, 43, 226)
]

# === DIMENSIONI SCHERMO === #
LARGHEZZA = DIM_GRIGLIA * (LATO_CASELLA + MARGINE) + MARGINE
ALTEZZA = LARGHEZZA + AREA_BLOCCHI_ALTEZZA

pygame.init()
screen = pygame.display.set_mode((LARGHEZZA, ALTEZZA))
pygame.display.set_caption("🧱 Block Blast")
clock = pygame.time.Clock()
font = pygame.font.SysFont("consolas", 26, bold=True)
font_big = pygame.font.SysFont("consolas", 40, bold=True)

# === SHAPES === #
BLOCCHI = {
    "1": [[1]],
    "2 orizzontale": [[1, 1]],
    "2 verticale": [[1], [1]],
    "3 orizzontale": [[1, 1, 1]],
    "3 verticale": [[1], [1], [1]],
    "2 cubo": [[1, 1], [1, 1]],
    "L dx": [[1, 0], [1, 0], [1, 1]],
    "L sx": [[0, 1], [0, 1], [1, 1]],
    "L dx down": [[1, 1], [1, 0], [1, 0]],
    "L sx down": [[1, 1], [0, 1], [0, 1]],
}

# === FUNZIONI === #

def crea_griglia():
    return [[0 for _ in range(DIM_GRIGLIA)] for _ in range(DIM_GRIGLIA)]

def genera_blocchi(n=3):
    return random.sample(list(BLOCCHI.keys()), n)

def disegna_griglia(griglia):
    for r in range(DIM_GRIGLIA):
        for c in range(DIM_GRIGLIA):
            x = c * (LATO_CASELLA + MARGINE) + MARGINE
            y = r * (LATO_CASELLA + MARGINE) + MARGINE
            colore = GRIGIO if griglia[r][c] == 0 else BIANCO
            pygame.draw.rect(screen, colore, (x, y, LATO_CASELLA, LATO_CASELLA), border_radius=6)

def disegna_blocco(shape, color):
    larg = len(shape[0]) * (LATO_CASELLA + MARGINE)
    alt = len(shape) * (LATO_CASELLA + MARGINE)
    surf = pygame.Surface((larg, alt), pygame.SRCALPHA)
    for r in range(len(shape)):
        for c in range(len(shape[r])):
            if shape[r][c] == 1:
                pygame.draw.rect(
                    surf, color,
                    (c * (LATO_CASELLA + MARGINE), r * (LATO_CASELLA + MARGINE),
                     LATO_CASELLA, LATO_CASELLA),
                    border_radius=6
                )
    return surf

def piazza_blocco(griglia, shape, r, c):
    # Controllo se il blocco entra nella griglia
    if r < 0 or c < 0:
        return False
    if r + len(shape) > DIM_GRIGLIA or c + len(shape[0]) > DIM_GRIGLIA:
        return False

    # Controllo collisioni
    for y in range(len(shape)):
        for x in range(len(shape[0])):
            if shape[y][x] == 1 and griglia[r + y][c + x] == 1:
                return False

    # Piazzamento
    for y in range(len(shape)):
        for x in range(len(shape[0])):
            if shape[y][x] == 1:
                griglia[r + y][c + x] = 1
    return True



def distruggi_linee(griglia):
    punti = 0
    righe_piene = [r for r in range(DIM_GRIGLIA) if all(griglia[r][c] == 1 for c in range(DIM_GRIGLIA))]
    colonne_piene = [c for c in range(DIM_GRIGLIA) if all(griglia[r][c] == 1 for r in range(DIM_GRIGLIA))]
    for r in righe_piene:
        griglia[r] = [0] * DIM_GRIGLIA
        punti += 100
    for c in colonne_piene:
        for r in range(DIM_GRIGLIA):
            griglia[r][c] = 0
        punti += 100
    return punti

def posizione_mouse_su_griglia(pos):
    x, y = pos
    for r in range(DIM_GRIGLIA):
        for c in range(DIM_GRIGLIA):
            rect = pygame.Rect(
                c * (LATO_CASELLA + MARGINE) + MARGINE,
                r * (LATO_CASELLA + MARGINE) + MARGINE,
                LATO_CASELLA, LATO_CASELLA
            )
            if rect.collidepoint(x, y):
                return r, c
    return None

def check_game_over(griglia, blocchi_grafica):
    for _, shape, _ in blocchi_grafica:
        for r in range(DIM_GRIGLIA):
            for c in range(DIM_GRIGLIA):
                if piazza_blocco([row[:] for row in griglia], shape, r, c):
                    return False
    return True

def messaggio_game_over(punti):
    running_msg = True
    btn_larghezza, btn_altezza = 200, 60
    btn_riavvia = pygame.Rect(LARGHEZZA//2 - btn_larghezza - 20, LARGHEZZA//2 + 40, btn_larghezza, btn_altezza)
    btn_esci = pygame.Rect(LARGHEZZA//2 + 20, LARGHEZZA//2 + 40, btn_larghezza, btn_altezza)

    while running_msg:
        screen.fill(GRIGIO_SCURO)

        text = font_big.render("HAI PERSO!", True, ROSSO)
        screen.blit(text, (LARGHEZZA//2 - text.get_width()//2, LARGHEZZA//2 - 100))

        punteggio_text = font.render(f"Punti ottenuti: {punti}", True, BIANCO)
        screen.blit(punteggio_text, (LARGHEZZA//2 - punteggio_text.get_width()//2, LARGHEZZA//2 - 40))

        pygame.draw.rect(screen, GIALLO, btn_riavvia, border_radius=12)
        pygame.draw.rect(screen, ROSSO, btn_esci, border_radius=12)

        text_riavvia = font.render("Riavvia", True, NERO)
        text_esci = font.render("Esci", True, NERO)
        screen.blit(text_riavvia, (btn_riavvia.centerx - text_riavvia.get_width()//2,
                                btn_riavvia.centery - text_riavvia.get_height()//2))
        screen.blit(text_esci, (btn_esci.centerx - text_esci.get_width()//2,
                                btn_esci.centery - text_esci.get_height()//2))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if btn_riavvia.collidepoint(mx, my):
                    return "restart"
                elif btn_esci.collidepoint(mx, my):
                    pygame.quit()
                    sys.exit()
def main():
    punti = 0

    while True:  
        griglia = crea_griglia()
        blocchi_correnti = genera_blocchi()
        blocchi_grafica = [(n, BLOCCHI[n], random.choice(COLORI_BLOCCHI)) for n in blocchi_correnti]
        dragging = False
        drag_index = None
        drag_offset = (0, 0)

        while True:  
            screen.fill(GRIGIO_SCURO)
            pygame.draw.rect(screen, NERO, (0, 0, LARGHEZZA, LARGHEZZA))
            pygame.draw.rect(screen, GRIGIO, (0, LARGHEZZA, LARGHEZZA, AREA_BLOCCHI_ALTEZZA))
            disegna_griglia(griglia)
 
            blocchi_surfaces = [disegna_blocco(shape, col) for _, shape, col in blocchi_grafica]
            larghezze = [surf.get_width() for surf in blocchi_surfaces]
            num_blocchi = len(blocchi_surfaces)
            total_width_blocchi = sum(larghezze)
            max_gap = 20
            gap = min(max_gap, (LARGHEZZA - total_width_blocchi) // (num_blocchi + 1))
            total_width_con_gap = total_width_blocchi + gap * (num_blocchi - 1)
            x_inizio = (LARGHEZZA - total_width_con_gap) // 2
            y_blocchi = LARGHEZZA + (AREA_BLOCCHI_ALTEZZA // 2) - 50

            blocchi_rects = []
            for surf in blocchi_surfaces:
                rect = pygame.Rect(x_inizio, y_blocchi, surf.get_width(), surf.get_height())
                blocchi_rects.append(rect)
                x_inizio += surf.get_width() + gap

            for i, (surf, rect) in enumerate(zip(blocchi_surfaces, blocchi_rects)):
                if dragging and drag_index == i:
                    mx, my = pygame.mouse.get_pos()
                    rect.x = mx - drag_offset[0]
                    rect.y = my - drag_offset[1]
                    ghost = disegna_blocco(blocchi_grafica[i][1], GHOST)
                    screen.blit(ghost, rect.topleft)
                screen.blit(surf, rect.topleft)
                if dragging and drag_index == i:
                    pygame.draw.rect(screen, GIALLO, rect.inflate(10, 10), 3)

            text = font.render(f"Punti: {punti}", True, BIANCO)
            screen.blit(text, (20, LARGHEZZA + AREA_BLOCCHI_ALTEZZA - 40))

            # Eventi
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = event.pos
                    if pos[1] > LARGHEZZA:
                        for i, rect in enumerate(blocchi_rects):
                            if rect.collidepoint(pos):
                                dragging = True
                                drag_index = i
                                drag_offset = (pos[0] - rect.x, pos[1] - rect.y)
                                break
                elif event.type == pygame.MOUSEBUTTONUP:
                    if dragging and drag_index is not None:
                        mx, my = pygame.mouse.get_pos()
                        nome, shape, colore = blocchi_grafica[drag_index]
                        cell = posizione_mouse_su_griglia((mx, my))
                        if cell:
                            r, c = cell
                            offset_righe = int(drag_offset[1] / (LATO_CASELLA + MARGINE))
                            offset_colonne = int(drag_offset[0] / (LATO_CASELLA + MARGINE))
                            r -= offset_righe
                            c -= offset_colonne
                            ok = piazza_blocco(griglia, shape, r, c)
                            if ok:
                                punti += distruggi_linee(griglia)
                                blocchi_grafica.pop(drag_index)
                                if not blocchi_grafica:
                                    blocchi_correnti = genera_blocchi()
                                    blocchi_grafica = [(n, BLOCCHI[n], random.choice(COLORI_BLOCCHI)) for n in blocchi_correnti]
                        dragging = False
                        drag_index = None

            if check_game_over(griglia, blocchi_grafica):
                result = messaggio_game_over(punti)
                if result == "restart":
                    punti = 0
                    break 

            pygame.display.flip()
            clock.tick(FPS)

if __name__ == "__main__":
    main()
