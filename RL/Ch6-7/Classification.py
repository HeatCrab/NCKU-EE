import os
os.makedirs("results", exist_ok=True)
import numpy as np
np.set_printoptions(threshold=np.inf)
import matplotlib.pyplot as plt
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torch.utils.data import DataLoader, TensorDataset

# Check if GPU is available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Generate Data
data_num = 100
data_dim = 2
data = 0.5 + 0.15 * np.random.randn(data_num, data_dim)
data[:,1] = data[:,1] - 1.0
temp = -0.5 + 0.2 * np.random.randn(data_num, data_dim)
data = np.concatenate((data, temp), axis=0)
temp = 0.35 + 0.25 * np.random.randn(data_num, data_dim)
data = np.concatenate((data, temp), axis=0)

# Generate labels
label = np.zeros(data_num)
temp = np.ones(data_num)
label = np.concatenate((label, temp), axis=0)
temp = 2 * np.ones(data_num)
label = np.concatenate((label, temp), axis=0)

num_classes = 3
data_num = data_num * 3

for i in range(data_num):
    # True labels (Show round dots in different colors)
    if label[i] == 0:
        plt.scatter(data[i,0], data[i,1], color="red", s=70, alpha=0.3)
    elif label[i] == 1:
        plt.scatter(data[i,0], data[i,1], color="green", s=70, alpha=0.3)
    elif label[i] == 2:
        plt.scatter(data[i,0], data[i,1], color="blue", s=70, alpha=0.3)
plt.savefig("results/data_distribution.png", dpi=150, bbox_inches="tight")
plt.close()

# Convert to PyTorch tensors
data_tensor = torch.FloatTensor(data).to(device)
labels_tensor = torch.LongTensor(label.astype(int)).to(device)

# Define Neural Network Model
class Classifier(nn.Module):
    def __init__(self, input_dim, hidden_dim, num_classes):
        super(Classifier, self).__init__()
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, hidden_dim)
        self.fc3 = nn.Linear(hidden_dim, num_classes)
        self.fc4 = nn.Linear(num_classes, num_classes)

    def forward(self, x):
        x = torch.tanh(self.fc1(x))
        x = torch.tanh(self.fc2(x))
        x = torch.tanh(self.fc3(x))
        x = self.fc4(x) # Remove Softmax layer for Loss function       
        return x
    
# Create model
model = Classifier(input_dim=2, hidden_dim=data_dim, num_classes=num_classes).to(device)
print(model)
print(f"\nNumber of model parameters: {sum(p.numel() for p in model.parameters() if p.requires_grad)}")

# Define loss function and optimizer
criterion = nn.CrossEntropyLoss()
optimizer = optim.SGD(model.parameters(), lr=0.1)

# Create data loader (batch size=1, 對應 original device)
dataset = TensorDataset(data_tensor, labels_tensor)
dataloader = DataLoader(dataset, batch_size=1, shuffle=True)

# Training loop
epochs = 20

for ep in range(epochs):
    model.train()
    train_loss = 0.0
    correct = 0

    # Train an epoch
    for batch_data, batch_labels in dataloader:
        optimizer.zero_grad()
        outputs = model(batch_data)
        loss = criterion(outputs, batch_labels)
        loss.backward()
        optimizer.step()

        train_loss += loss.item()
        pred = outputs.argmax(dim=1)
        correct += (pred == batch_labels).sum().item()

    # Calculate total accuracy
    accuracy = correct / data_num
    avg_loss = train_loss / data_num

    print(f"Epoch [{ep+1}/{epochs}], Loss: {avg_loss:.4f}, Accuracy: {accuracy:.4f}")

    # Visualize decision boundaries
    model.eval()
    with torch.no_grad():
        logits = model(data_tensor)
        y_pred = F.softmax(logits, dim=1) # Apply Softmax to get probabilities
        result = logits.argmax(dim=1).cpu().numpy()

    # Clear last plt
    plt.cla()

    # Plot data points
    for i in range(data_num):
        # Real labels (Show round dots in different colors)
        if result[i] == 0:
            plt.scatter(data[i,0], data[i,1], color="red", s=70, alpha=0.3)
        elif result[i] == 1:
            plt.scatter(data[i,0], data[i,1], color="green", s=70, alpha=0.3)
        elif result[i] == 2:
            plt.scatter(data[i,0], data[i,1], color="blue", s=70, alpha=0.3)
        
        # Predicted labels (Show 十字 in different colors)
        if label[i] == 0:
            plt.scatter(data[i,0], data[i,1], color="red", s=70, alpha=0.8, marker="+")
        elif label[i] == 1:
            plt.scatter(data[i,0], data[i,1], color="green", s=70, alpha=0.8, marker="+")
        elif label[i] == 2:
            plt.scatter(data[i,0], data[i,1], color="blue", s=70, alpha=0.8, marker="+")

    plt.grid()
    plt.title(f"Epoch {ep+1} - Accuracy: {accuracy:.4f}")
    if ep == epochs - 1:
        plt.savefig("results/classification_result.png", dpi=150, bbox_inches="tight")
    plt.close()