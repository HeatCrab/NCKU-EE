# -*- coding: utf-8 -*-
import gymnasium as gym
from gymnasium import spaces
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import time
import torch
import warnings
warnings.filterwarnings('ignore')


class CircleTrackingEnv(gym.Env):
    """兩輪移動機器人追圓環境"""
    
    def __init__(self, render_mode=None):
        super(CircleTrackingEnv, self).__init__()
        
        # 可跟StableBaseline對應
        self.render_mode = render_mode
        
        # 環境參數
        self.dt = 0.1  # 時間步長
        self.max_steps = 200  # 每個episode最大步數
        self.wheel_base = 0.3  # 兩輪間距
        
        # 圓的參數
        self.circle_center = np.array([0.0, 0.0])
        self.circle_radius = 2.0
        self.target_angular_velocity = 0.5  # 目標角速度
        
        # 機器人狀態 [x, y, theta]
        self.robot_state = None
        self.current_step = 0
        
        # 可跟StableBaseline對應
        # 觀測空間: [dx, dy, dtheta, dist_to_circle]
        self.observation_space = spaces.Box(
            low=-np.inf,
            high=np.inf,
            shape=(4,),
            dtype=np.float32
        )
        
        # 可跟StableBaseline對應
        # 動作空間: [linear_velocity, angular_velocity]
        # linear_velocity: 線速度，只能前進 [0, 1.0] m/s
        # angular_velocity: 角速度，左右轉 [-1.0, 1.0] rad/s
        self.action_space = spaces.Box(
            low=np.array([0.0, -1.0]),    # 線速度>=0 (不能後退), 角速度可左右
            high=np.array([1.0, 1.0]),    # 限制最大速度
            shape=(2,),
            dtype=np.float32
        )
        
        # 可視化相關
        self.fig = None
        self.ax = None
        self.step_counter = 0
        
        # 如果需要渲染，立即初始化
        if render_mode == "human":
            self._init_render()
    
    def _init_render(self):
        """初始化渲染"""
        if self.fig is None:
            self.fig = plt.figure(figsize=(5, 5))
            self.ax = self.fig.add_subplot(111)
        
    # 可跟StableBaseline對應
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        
        # 隨機初始化機器人位置（更靠近圓）
        angle = np.random.uniform(0, 2*np.pi)
        distance = self.circle_radius + np.random.uniform(0.2, 0.6)  # 改成0.2~0.6，更靠近
        
        x = self.circle_center[0] + distance * np.cos(angle)
        y = self.circle_center[1] + distance * np.sin(angle)
        
        # 初始方向設為大致朝向切線方向（加上小擾動）
        tangent_angle = angle + np.pi/2  # 切線方向
        theta = tangent_angle + np.random.uniform(-np.pi/6, np.pi/6)  # 加上±30度擾動
        
        self.robot_state = np.array([x, y, theta], dtype=np.float32)
        self.current_step = 0
        self.prev_distance_error = self._get_distance_to_circle()
        
        return self._get_observation(), {}
    
    def _get_distance_to_circle(self):
        """計算機器人到圓的距離"""
        robot_pos = self.robot_state[:2]
        dist_to_center = np.linalg.norm(robot_pos - self.circle_center)
        return abs(dist_to_center - self.circle_radius)
    
    def _get_observation(self):
        """獲取觀測值"""
        robot_pos = self.robot_state[:2]
        robot_theta = self.robot_state[2]
        
        # 到圓心的向量
        to_center = self.circle_center - robot_pos
        dist_to_center = np.linalg.norm(to_center)
        
        # 計算圓上最近點
        if dist_to_center > 0:
            closest_point_on_circle = self.circle_center + (to_center / dist_to_center) * self.circle_radius
        else:
            closest_point_on_circle = self.circle_center + np.array([self.circle_radius, 0])
        
        # 相對位置
        dx = closest_point_on_circle[0] - robot_pos[0]
        dy = closest_point_on_circle[1] - robot_pos[1]
        
        # 目標角度（切線方向）切線角度的垂直方向也就是切線角度+90度
        tangent_angle = np.arctan2(to_center[1], to_center[0]) + np.pi/2
        dtheta = self._angle_diff(tangent_angle, robot_theta)
        
        # 距離誤差
        dist_error = self._get_distance_to_circle()
        
        obs = np.array([dx, dy, dtheta, dist_error], dtype=np.float32)
        return obs
    
    def _angle_diff(self, target, current):
        """計算角度差，範圍[-pi, pi]"""
        diff = target - current
        while diff > np.pi:
            diff -= 2*np.pi
        while diff < -np.pi:
            diff += 2*np.pi
        return diff
    
    # 可跟StableBaseline對應
    def step(self, action):
        # 解析動作：線速度和角速度
        v = np.clip(action[0], 0.0, 1.0)      # 線速度 (只能前進)
        omega = np.clip(action[1], -1.0, 1.0)  # 角速度 (左右轉)
        
        # 更新機器人狀態
        x, y, theta = self.robot_state
        x += v * np.cos(theta) * self.dt
        y += v * np.sin(theta) * self.dt
        theta += omega * self.dt
        
        # 角度歸一化
        theta = np.arctan2(np.sin(theta), np.cos(theta))
        
        self.robot_state = np.array([x, y, theta], dtype=np.float32)
        self.current_step += 1
        
        # 計算獎勵
        reward = self._compute_reward(v, omega)
        
        """
        terminated vs truncated 的區別
        在 Gymnasium (gym 的新版本) 中，episode 結束有兩種情況：
        1. terminated (終止)
        表示 episode 因為達成某個終止條件而自然結束，例如：
        A.任務成功完成
        B.任務失敗（例如：機器人掉下懸崖、碰撞）
        C.違反某些規則
        2. truncated (截斷)
        表示 episode 因為達到最大步數限制而被強制結束，但任務本身還沒有成功或失敗：
        為什麼要區分？
        這個區分對強化學習訓練很重要：
        python# 在計算 return 時的處理不同
        if terminated:
            # 任務真的結束了，不需要估計未來價值
            next_value = 0
        elif truncated:
            # 任務還沒結束，需要用價值函數估計剩餘價值
            next_value = value_function(next_state)
        """
        
        # 檢查是否結束
        terminated = False
        truncated = self.current_step >= self.max_steps   # 達到200步就截斷
        
        # 檢查是否太遠
        dist_to_center = np.linalg.norm(self.robot_state[:2] - self.circle_center)
        if dist_to_center > self.circle_radius + 5.0:
            terminated = True
            # reward -= 50.0
            
        obs = self._get_observation()
        
        # 自動渲染（如果啟用）
        if self.render_mode == "human":
            self.step_counter += 1
            if self.step_counter % 3 == 0:  # 每3步渲染一次
                self.render()
        
        return obs, reward, terminated, truncated, {}
    
    def _compute_reward(self, v, omega):
        # Dense reward for circle tracking, combining three shaped terms.
        dist_error = self._get_distance_to_circle()

        # Heading error relative to the circle's tangent direction.
        robot_pos = self.robot_state[:2]
        to_center = self.circle_center - robot_pos
        tangent_angle = np.arctan2(to_center[1], to_center[0]) + np.pi/2
        heading_error = abs(self._angle_diff(tangent_angle, self.robot_state[2]))

        # Stay on the circle: peaks at 1 when on the line, decays with distance.
        position_reward = np.exp(-3.0 * dist_error)
        # Face along the tangent: peaks at 1 when aligned, decays with heading error.
        heading_reward = np.exp(-1.0 * heading_error)
        # Move forward along the circle; cos turns negative when facing away,
        # so driving while misaligned is penalised.
        progress_reward = v * np.cos(heading_error)

        reward = 50.0 * position_reward + 30.0 * heading_reward + 20.0 * progress_reward
        return reward
    
    def render(self):
        if self.render_mode != "human":
            return
        
        if self.fig is None:
            self._init_render()
        
        # 清空並重繪
        self.ax.clear()
        
        # 繪製圓
        circle = plt.Circle(self.circle_center, self.circle_radius, 
                           color='blue', fill=False, linewidth=3, label='Target Circle')
        self.ax.add_patch(circle)
        
        # 繪製機器人
        x, y, theta = self.robot_state
        
        # 機器人本體（三角形）
        robot_length = 0.4
        robot_width = 0.25
        
        # 計算三角形頂點
        front_x = x + robot_length * np.cos(theta)
        front_y = y + robot_length * np.sin(theta)
        
        left_x = x + robot_width/2 * np.cos(theta + np.pi/2)
        left_y = y + robot_width/2 * np.sin(theta + np.pi/2)
        
        right_x = x + robot_width/2 * np.cos(theta - np.pi/2)
        right_y = y + robot_width/2 * np.sin(theta - np.pi/2)
        
        triangle = plt.Polygon([[front_x, front_y], [left_x, left_y], [right_x, right_y]], 
                              color='red', alpha=0.8, label='Robot')
        self.ax.add_patch(triangle)
        
        # 繪製方向箭頭
        arrow_length = 0.6
        self.ax.arrow(x, y, arrow_length*np.cos(theta), arrow_length*np.sin(theta),
                     head_width=0.25, head_length=0.2, fc='darkred', ec='darkred', linewidth=2)
        
        # 繪製機器人位置點
        self.ax.plot(x, y, 'ro', markersize=3)
        
        # 設置坐標軸
        limit = self.circle_radius + 2
        self.ax.set_xlim(-limit, limit)
        self.ax.set_ylim(-limit, limit)
        self.ax.set_aspect('equal')
        self.ax.grid(True, alpha=0.3, linestyle='--')
        self.ax.set_xlabel('X (m)', fontsize=9)
        self.ax.set_ylabel('Y (m)', fontsize=9)
        
        # 顯示距離資訊
        dist_error = self._get_distance_to_circle()
        self.ax.set_title(f'Robot Circle Tracking\nStep: {self.current_step} | Distance Error: {dist_error:.3f}m', 
                         fontsize=10, fontweight='bold')
        
        self.ax.legend(loc='upper right', fontsize=8)
        
        # self.fig = None  # 重置，下次會重新創建
        plt.show()  # 顯示圖片到 Spyder Plots
        plt.close(self.fig)  # 關閉避免記憶體累積
        self.fig = None  # 重置，下次會重新創建
        self.ax = None   # 也要重置 ax


    def close(self):
        if self.fig is not None:
            plt.close(self.fig)
            self.fig = None
            self.ax = None


if __name__ == "__main__":
    
    # Check device availability
    device = torch.device(
        "cuda" if torch.cuda.is_available() else
        "mps" if torch.backends.mps.is_available() else
        "cpu"
    )
    print(f"Using device: {device}")
    print(f"Matplotlib backend: {matplotlib.get_backend()}")
    
    # 創建環境
    env = CircleTrackingEnv(render_mode="human")
    env.reset()
    
    for i in range(20):
        action = env.action_space.sample()
        env.step(action)
    
    env.close()
    