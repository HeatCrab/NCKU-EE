# -*- coding: utf-8 -*-
import gymnasium as gym
import math
import random
import matplotlib
import matplotlib.pyplot as plt
from collections import namedtuple, deque
from itertools import count
import time
import numpy as np
import os

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import pygame

# 主要執行程式
if __name__ == "__main__":
    
    # 初始化pygame
    pygame.init()
    
    # 創建環境
    env = gym.make("CartPole-v1", render_mode="human")
    
    # 開始新回合
    state, info = env.reset()
    print(f"初始狀態: {state}")
    print("控制說明：按 A 或 ← 向左推車，按 D 或 → 向右推車，按 Q 退出")
    
    total_reward = 0
    step_count = 0
    
    # 遊戲主循環
    while True:
        
        # /////////////鍵盤控制////////////////
        # 處理pygame事件
        action = None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                break
            elif event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_a, pygame.K_LEFT]:
                    action = 0  # 向左
                elif event.key in [pygame.K_d, pygame.K_RIGHT]:
                    action = 1  # 向右
                elif event.key == pygame.K_q:
                    action = -1  # 退出
        
        # 檢查鍵盤狀態（持續按鍵）
        keys = pygame.key.get_pressed()
        if action is None:
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                action = 0  # 向左
            elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                action = 1  # 向右
        
        # 如果沒有按鍵，跳過這次循環
        if action is None:
            time.sleep(0.01)
            continue
        
        # 退出遊戲
        if action == -1:
            break
            
        print(f"步驟 {step_count}: 執行動作 {action}")
        # /////////////鍵盤控制////////////////
        
        # 執行動作，獲取反饋
        state, reward, terminated, truncated, info = env.step(action)
        
        # state = [0.12, -0.34, 0.05, 0.89]
        #           ↑     ↑      ↑     ↑
        #       小車位置 小車速度 桿角度 桿角速度
        
        # 更新統計
        total_reward += reward
        step_count += 1
        
        print(f"  新狀態: {state}")
        print(f"  獎勵: {reward}")
        print(f"  正常結束: {terminated}")
        print(f"  時間截斷: {truncated}")
        print(f"  總獎勵: {total_reward}")
        print("-" * 40)
        
        # 檢查遊戲是否結束
        if terminated or truncated:
            print(f"遊戲結束！")
            print(f"原因: {'正常結束' if terminated else '達到時間限制'}")
            print(f"總步數: {step_count}")
            print(f"總獎勵: {total_reward}")
            break
        
        time.sleep(0.05)  # 稍微放慢速度便於控制

    env.close()
    pygame.quit()