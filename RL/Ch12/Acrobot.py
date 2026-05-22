# -*- coding: utf-8 -*-
import gymnasium as gym
import pygame
import numpy as np
import matplotlib.pyplot as plt
import time
import torch
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.callbacks import BaseCallback
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.evaluation import evaluate_policy
import warnings
warnings.filterwarnings('ignore')

# 主要執行程式
if __name__ == "__main__":
    
    # 初始化pygame用於鍵盤輸入
    pygame.init()
    
    # 創建Acrobot環境（帶視覺渲染）
    env = gym.make("Acrobot-v1", render_mode="human")
    
    print("鍵盤控制說明:")
    print("← (左箭頭): 向左施力 (action=0)")
    print("→ (右箭頭): 向右施力 (action=2)")
    print("↑ (上箭頭): 無動作 (action=1)")
    print("ESC: 退出")
    print("R: 重置環境")
    print("\n開始遊戲...")
    
    # 重置環境
    obs, info = env.reset()
    total_reward = 0
    steps = 0
    
    # 遊戲主循環
    try:
        while True:
            # 處理pygame事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    raise KeyboardInterrupt
            
            # 獲取按鍵狀態
            keys = pygame.key.get_pressed()
            
            # 根據按鍵選擇動作
            action = 1  # 默認無動作
            
            if keys[pygame.K_LEFT]:
                action = 0  # 向左施力
            elif keys[pygame.K_RIGHT]:
                action = 2  # 向右施力
            elif keys[pygame.K_UP]:
                action = 1  # 無動作
            elif keys[pygame.K_r]:
                # 重置環境
                obs, info = env.reset()
                total_reward = 0
                steps = 0
                print(f"\n環境已重置")
                time.sleep(0.2)  # 避免重複觸發
            elif keys[pygame.K_ESCAPE]:
                break
            
            # 執行動作
            obs, reward, terminated, truncated, info = env.step(action)
            total_reward += reward
            steps += 1
            
            # 顯示當前狀態
            if steps % 50 == 0:  # 每50步顯示一次
                print(f"步數: {steps}, 累積獎勵: {total_reward:.2f}")
            
            # 檢查是否結束
            if terminated or truncated:
                if total_reward > -100:
                    print(f"\n成功！步數: {steps}, 獎勵: {total_reward:.2f}")
                else:
                    print(f"\n失敗，步數: {steps}, 獎勵: {total_reward:.2f}")
                
                # 自動重置
                obs, info = env.reset()
                total_reward = 0
                steps = 0
                print("自動重置環境，繼續遊戲...")
            
            # 控制遊戲速度
            time.sleep(0.02)
    
    except KeyboardInterrupt:
        print("\n遊戲結束！")
    
    finally:
        env.close()
        pygame.quit()