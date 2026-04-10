import os
import matplotlib.pyplot as plt
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset

os.makedirs("results", exist_ok=True)

# Set up device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Data generation
x_train = np.arange(0, 1, 0.01)
y_train = np.sin(2 * np.pi * x_train)
plt.plot(x_train, y_train, linestyle="-", label="Ground Truth")
plt.xlabel("x")
plt.ylabel("f(x)")
plt.savefig("results/ground_truth.png", dpi=150, bbox_inches="tight")
plt.close()

# Convert to PyTorch tensors
x_train_tensor = torch.FloatTensor(x_train.reshape(-1, 1)).to(device)
y_train_tensor = torch.FloatTensor(y_train.reshape(-1, 1)).to(device)

# Create data loader
dataset = TensorDataset(x_train_tensor, y_train_tensor)
dataloader = DataLoader(dataset, batch_size=1, shuffle=True)

batch_size = 1
epochs = 1000

# Create model
class NeuralNetwork(nn.Module):
    def __init__(self):
        super(NeuralNetwork, self).__init__()
        self.layers = nn.Sequential(
            nn.Linear(1, 5),
            nn.Tanh(),
            nn.Linear(5, 5),
            nn.Tanh(),
            nn.Linear(5, 1)
        )

    def forward(self, x):
        return self.layers(x)
    
model = NeuralNetwork().to(device)

# Define loss function and optimizer
criterion = nn.MSELoss()
optimizer = optim.Adam(model.parameters(), lr=0.01)

loss_arr = []
for epoch in range(epochs):
    epoch_loss = 0.0
    num_batches = 0

    model.train()
    for batch_x, batch_y in dataloader:
        # forward propagation
        outputs = model(batch_x)
        loss = criterion(outputs, batch_y)

        # backward propagation and optimization
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        epoch_loss += loss.item()
        num_batches += 1

    # Record average loss
    avg_loss = epoch_loss / num_batches
    loss_arr.append(avg_loss)

    print(f"Epoch [{epoch+1}/{epochs}], Loss: {avg_loss:.6f}")

# Test
model.eval()
with torch.no_grad():
    x_test = torch.FloatTensor(x_train.reshape(-1, 1)).to(device)
    y_pred = model(x_test)
    y_pred_np = y_pred.cpu().numpy().flatten()

# Plot
plt.subplot(211)
plt.plot(x_train, y_train, linestyle="-", label="Ground Truth")
plt.plot(x_train, y_pred_np, linestyle="-", label="Prediction")
plt.title('Epoch:' + str(epochs))
plt.legend()

plt.subplot(212)
plt.plot(loss_arr, label='Loss value')
plt.title('Learning Curve')
plt.legend()

plt.tight_layout()
plt.savefig("results/prediction.png", dpi=150, bbox_inches="tight")
plt.close()