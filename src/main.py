# file: main.py

import pygame
import sys
from ui.constants import WIN_W, WIN_H, C_TEXT_MUTED
from game.game import Game
from ui.renderer import GameRenderer
from ui.input_handler import InputHandler

AI_MOVE_DELAY_MS = 500   # milliseconds to wait before AI moves


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIN_W, WIN_H))
    pygame.display.set_caption("Quoridor")
    clock = pygame.time.Clock()

    renderer = GameRenderer(screen)

    # ── Application state ─────────────────────────────────────────────────
    app_state = 'main_menu'        # 'main_menu' | 'difficulty_menu' | 'playing'
    game    = None
    handler = None

    while True:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # ── Main menu ─────────────────────────────────────────────────
            if app_state == 'main_menu':
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    btn = renderer.get_menu_button_at(mouse_pos)
                    if btn == 'pvp':
                        game = Game(game_mode='pvp')
                        handler = InputHandler(game, renderer)
                        game.set_message(
                            "Player 1's turn  -  press M / H / V to switch mode",
                            C_TEXT_MUTED)
                        app_state = 'playing'
                    elif btn == 'ai':
                        app_state = 'difficulty_menu'

            # ── Difficulty menu ───────────────────────────────────────────
            elif app_state == 'difficulty_menu':
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    btn = renderer.get_difficulty_button_at(mouse_pos)
                    if btn in ('easy', 'medium', 'hard'):
                        game = Game(game_mode='ai', ai_difficulty=btn)
                        handler = InputHandler(game, renderer)
                        game.set_message(
                            "Your turn  -  press M / H / V to switch mode",
                            C_TEXT_MUTED)
                        app_state = 'playing'
                    elif btn == 'back':
                        app_state = 'main_menu'
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    app_state = 'main_menu'

            # ── Playing ───────────────────────────────────────────────────
            elif app_state == 'playing':
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        app_state = 'main_menu'
                        game = None
                        handler = None
                        continue
                    handler.handle_key(event.key)
                elif event.type == pygame.MOUSEMOTION:
                    handler.handle_mouse_motion(event.pos)
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    handler.handle_mouse_click(event.pos)

        # ── Render current screen ─────────────────────────────────────────
        if app_state == 'main_menu':
            renderer.draw_menu(mouse_pos)

        elif app_state == 'difficulty_menu':
            renderer.draw_difficulty_menu(mouse_pos)

        elif app_state == 'playing':
            # AI turn with delay
            if game.is_ai_turn():
                now = pygame.time.get_ticks()
                if game.ai_turn_start is None:
                    game.ai_turn_start = now
                elif now - game.ai_turn_start >= AI_MOVE_DELAY_MS:
                    game.do_ai_move()

            renderer.draw(game, handler.ui_state(mouse_pos))

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
