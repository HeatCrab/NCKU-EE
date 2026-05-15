# -*- coding: utf-8 -*-
import gymnasium as gym
import numpy as np
import pygame

# 主要執行程式
if __name__ == "__main__":
    # 初始化 pygame
    pygame.init()
    
    # 建立環境
    env = gym.make("MountainCarContinuous-v0", render_mode="human")
    state, _ = env.reset()
    
    print("鍵盤控制說明:")
    print("A/左箭頭 = 向左推")
    print("D/右箭頭 = 向右推") 
    print("其他鍵 = 不動")
    print("ESC/關閉視窗 = 退出")
    
    try:
        while True:
            # 處理 pygame 事件
            action = [0.0]  # 預設不動
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    raise KeyboardInterrupt
            
            # 檢查按鍵狀態
            keys = pygame.key.get_pressed()
            
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                action = [-1.0]  # 向左推
            elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                action = [1.0]   # 向右推
            elif keys[pygame.K_ESCAPE]:
                raise KeyboardInterrupt
            
            # 執行動作
            state, reward, terminated, truncated, _ = env.step(action)
            
            # 如果遊戲結束就重新開始
            if terminated or truncated:
                print(f"重新開始! 位置: {state[0]:.3f}")
                state, _ = env.reset()
                
    except KeyboardInterrupt:
        print("\n演示結束！")
    
    pygame.quit()
    env.close()