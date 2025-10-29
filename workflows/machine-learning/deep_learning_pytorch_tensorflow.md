# Deep Learning with PyTorch & TensorFlow

**ID:** mac-004  
**Category:** Machine Learning  
**Priority:** MEDIUM  
**Complexity:** Advanced  
**Estimated Time:** 120-180 minutes  
**Last Updated:** 2025-10-26

---

## Purpose

**What:** Build, train, and deploy deep learning models using PyTorch and TensorFlow for computer vision, NLP, and other deep learning tasks

**Why:** Deep learning enables solving complex problems like image recognition, natural language understanding, and time series prediction that traditional ML struggles with

**When to use:**
- Image classification/segmentation
- Natural language processing
- Time series forecasting
- Speech recognition
- Generative models
- Transfer learning
- Complex pattern recognition
- High-dimensional data

---

## Prerequisites

**Required:**
- [ ] Python 3.8+ with PyTorch or TensorFlow
- [ ] CUDA-capable GPU (recommended)
- [ ] Understanding of neural networks
- [ ] Linear algebra basics
- [ ] Data preprocessing knowledge
- [ ] GPU drivers installed

**Check before starting:**
```bash
# Check PyTorch installation
python -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}')"

# Check TensorFlow installation
python -c "import tensorflow as tf; print(f'TensorFlow: {tf.__version__}'); print(f'GPU devices: {tf.config.list_physical_devices(\"GPU\")}')"

# Check CUDA
nvidia-smi
```

---

## Implementation Steps

### Step 1: Set Up PyTorch Project Structure

**What:** Create a well-organized PyTorch project with proper structure

**How:**

**Project Structure:**
```
deep-learning-project/
├── data/
│   ├── raw/
│   ├── processed/
│   └── external/
├── models/
│   ├── __init__.py
│   ├── cnn.py
│   ├── rnn.py
│   └── transformer.py
├── src/
│   ├── __init__.py
│   ├── data/
│   │   ├── dataset.py
│   │   └── transforms.py
│   ├── models/
│   │   ├── architecture.py
│   │   └── pretrained.py
│   ├── training/
│   │   ├── trainer.py
│   │   └── callbacks.py
│   └── utils/
│       ├── metrics.py
│       └── visualization.py
├── configs/
│   └── config.yaml
├── notebooks/
├── tests/
└── requirements.txt
```

**Base PyTorch Model Template:**
```python
# src/models/base_model.py
"""
Base PyTorch model template
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from abc import ABC, abstractmethod

class BaseModel(nn.Module, ABC):
    """Base class for PyTorch models."""
    
    def __init__(self):
        super(BaseModel, self).__init__()
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    @abstractmethod
    def forward(self, x):
        """Forward pass - must be implemented by subclasses."""
        pass
    
    def count_parameters(self):
        """Count trainable parameters."""
        return sum(p.numel() for p in self.parameters() if p.requires_grad)
    
    def save_checkpoint(self, filepath, epoch, optimizer, loss):
        """Save model checkpoint."""
        torch.save({
            'epoch': epoch,
            'model_state_dict': self.state_dict(),
            'optimizer_state_dict': optimizer.state_dict(),
            'loss': loss,
        }, filepath)
        print(f"✅ Checkpoint saved to {filepath}")
    
    def load_checkpoint(self, filepath, optimizer=None):
        """Load model checkpoint."""
        checkpoint = torch.load(filepath, map_location=self.device)
        self.load_state_dict(checkpoint['model_state_dict'])
        
        if optimizer:
            optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        
        print(f"✅ Checkpoint loaded from {filepath}")
        return checkpoint['epoch'], checkpoint['loss']
```

**CNN Architecture Example:**
```python
# models/cnn.py
"""
Convolutional Neural Network for image classification
"""

import torch.nn as nn
import torch.nn.functional as F

class CNN(BaseModel):
    """CNN for image classification."""
    
    def __init__(self, num_classes=10, input_channels=3):
        super(CNN, self).__init__()
        
        # Convolutional layers
        self.conv1 = nn.Conv2d(input_channels, 32, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm2d(32)
        
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm2d(64)
        
        self.conv3 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        self.bn3 = nn.BatchNorm2d(128)
        
        # Pooling
        self.pool = nn.MaxPool2d(2, 2)
        
        # Dropout
        self.dropout = nn.Dropout(0.5)
        
        # Fully connected layers
        self.fc1 = nn.Linear(128 * 4 * 4, 512)  # Assuming 32x32 input
        self.fc2 = nn.Linear(512, num_classes)
    
    def forward(self, x):
        # Conv block 1
        x = self.pool(F.relu(self.bn1(self.conv1(x))))
        
        # Conv block 2
        x = self.pool(F.relu(self.bn2(self.conv2(x))))
        
        # Conv block 3
        x = self.pool(F.relu(self.bn3(self.conv3(x))))
        
        # Flatten
        x = x.view(-1, 128 * 4 * 4)
        
        # Fully connected
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.fc2(x)
        
        return x

# Usage
model = CNN(num_classes=10)
print(f"Parameters: {model.count_parameters():,}")
```

**ResNet Implementation:**
```python
# models/resnet.py
"""
ResNet implementation
"""

import torch.nn as nn

class ResidualBlock(nn.Module):
    """Residual block with skip connection."""
    
    def __init__(self, in_channels, out_channels, stride=1):
        super(ResidualBlock, self).__init__()
        
        self.conv1 = nn.Conv2d(in_channels, out_channels, kernel_size=3, 
                               stride=stride, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(out_channels)
        
        self.conv2 = nn.Conv2d(out_channels, out_channels, kernel_size=3,
                               stride=1, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(out_channels)
        
        # Skip connection
        self.skip = nn.Sequential()
        if stride != 1 or in_channels != out_channels:
            self.skip = nn.Sequential(
                nn.Conv2d(in_channels, out_channels, kernel_size=1, 
                         stride=stride, bias=False),
                nn.BatchNorm2d(out_channels)
            )
    
    def forward(self, x):
        identity = x
        
        out = F.relu(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))
        
        out += self.skip(identity)
        out = F.relu(out)
        
        return out

class ResNet(BaseModel):
    """ResNet architecture."""
    
    def __init__(self, num_classes=10, num_blocks=[2, 2, 2, 2]):
        super(ResNet, self).__init__()
        
        self.in_channels = 64
        
        self.conv1 = nn.Conv2d(3, 64, kernel_size=7, stride=2, padding=3, bias=False)
        self.bn1 = nn.BatchNorm2d(64)
        self.maxpool = nn.MaxPool2d(kernel_size=3, stride=2, padding=1)
        
        self.layer1 = self._make_layer(64, num_blocks[0], stride=1)
        self.layer2 = self._make_layer(128, num_blocks[1], stride=2)
        self.layer3 = self._make_layer(256, num_blocks[2], stride=2)
        self.layer4 = self._make_layer(512, num_blocks[3], stride=2)
        
        self.avgpool = nn.AdaptiveAvgPool2d((1, 1))
        self.fc = nn.Linear(512, num_classes)
    
    def _make_layer(self, out_channels, num_blocks, stride):
        layers = []
        layers.append(ResidualBlock(self.in_channels, out_channels, stride))
        self.in_channels = out_channels
        
        for _ in range(1, num_blocks):
            layers.append(ResidualBlock(out_channels, out_channels))
        
        return nn.Sequential(*layers)
    
    def forward(self, x):
        x = F.relu(self.bn1(self.conv1(x)))
        x = self.maxpool(x)
        
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)
        
        x = self.avgpool(x)
        x = x.view(x.size(0), -1)
        x = self.fc(x)
        
        return x
```

**Verification:**
- [ ] PyTorch installed
- [ ] GPU accessible
- [ ] Models defined
- [ ] Forward pass working
- [ ] Parameter counting correct

**If This Fails:**
→ Check PyTorch installation
→ Verify CUDA setup
→ Review model architecture
→ Test with dummy data
→ Check tensor shapes

---

### Step 2: Implement PyTorch Training Loop

**What:** Create comprehensive training loop with validation and checkpointing

**How:**

**Training Framework:**
```python
# src/training/trainer.py
"""
PyTorch training framework
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from tqdm import tqdm
import numpy as np
import logging
from pathlib import Path
import mlflow

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Trainer:
    """PyTorch model trainer."""
    
    def __init__(self, model, train_loader, val_loader, config):
        """
        Initialize trainer.
        
        Args:
            model: PyTorch model
            train_loader: Training data loader
            val_loader: Validation data loader
            config: Training configuration
        """
        self.model = model
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.config = config
        
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)
        
        # Loss function
        self.criterion = self._get_criterion()
        
        # Optimizer
        self.optimizer = self._get_optimizer()
        
        # Learning rate scheduler
        self.scheduler = self._get_scheduler()
        
        # Metrics
        self.train_losses = []
        self.val_losses = []
        self.val_accuracies = []
        
        # MLflow
        mlflow.set_experiment(config.get('experiment_name', 'deep_learning'))
    
    def _get_criterion(self):
        """Get loss function."""
        loss_name = self.config.get('loss', 'cross_entropy')
        
        if loss_name == 'cross_entropy':
            return nn.CrossEntropyLoss()
        elif loss_name == 'mse':
            return nn.MSELoss()
        elif loss_name == 'bce':
            return nn.BCEWithLogitsLoss()
        else:
            raise ValueError(f"Unknown loss: {loss_name}")
    
    def _get_optimizer(self):
        """Get optimizer."""
        opt_name = self.config.get('optimizer', 'adam')
        lr = self.config.get('learning_rate', 0.001)
        
        if opt_name == 'adam':
            return optim.Adam(self.model.parameters(), lr=lr)
        elif opt_name == 'sgd':
            return optim.SGD(self.model.parameters(), lr=lr, 
                           momentum=self.config.get('momentum', 0.9))
        elif opt_name == 'adamw':
            return optim.AdamW(self.model.parameters(), lr=lr,
                             weight_decay=self.config.get('weight_decay', 0.01))
        else:
            raise ValueError(f"Unknown optimizer: {opt_name}")
    
    def _get_scheduler(self):
        """Get learning rate scheduler."""
        scheduler_name = self.config.get('scheduler', None)
        
        if scheduler_name == 'step':
            return optim.lr_scheduler.StepLR(
                self.optimizer,
                step_size=self.config.get('step_size', 10),
                gamma=self.config.get('gamma', 0.1)
            )
        elif scheduler_name == 'cosine':
            return optim.lr_scheduler.CosineAnnealingLR(
                self.optimizer,
                T_max=self.config.get('epochs', 100)
            )
        elif scheduler_name == 'reduce_on_plateau':
            return optim.lr_scheduler.ReduceLROnPlateau(
                self.optimizer,
                mode='min',
                patience=self.config.get('patience', 5)
            )
        
        return None
    
    def train_epoch(self):
        """Train for one epoch."""
        self.model.train()
        
        running_loss = 0.0
        correct = 0
        total = 0
        
        pbar = tqdm(self.train_loader, desc="Training")
        
        for batch_idx, (data, target) in enumerate(pbar):
            data, target = data.to(self.device), target.to(self.device)
            
            # Forward pass
            self.optimizer.zero_grad()
            output = self.model(data)
            loss = self.criterion(output, target)
            
            # Backward pass
            loss.backward()
            self.optimizer.step()
            
            # Metrics
            running_loss += loss.item()
            _, predicted = output.max(1)
            total += target.size(0)
            correct += predicted.eq(target).sum().item()
            
            # Update progress bar
            pbar.set_postfix({
                'loss': running_loss / (batch_idx + 1),
                'acc': 100. * correct / total
            })
        
        epoch_loss = running_loss / len(self.train_loader)
        epoch_acc = 100. * correct / total
        
        return epoch_loss, epoch_acc
    
    def validate(self):
        """Validate model."""
        self.model.eval()
        
        running_loss = 0.0
        correct = 0
        total = 0
        
        with torch.no_grad():
            for data, target in tqdm(self.val_loader, desc="Validation"):
                data, target = data.to(self.device), target.to(self.device)
                
                output = self.model(data)
                loss = self.criterion(output, target)
                
                running_loss += loss.item()
                _, predicted = output.max(1)
                total += target.size(0)
                correct += predicted.eq(target).sum().item()
        
        val_loss = running_loss / len(self.val_loader)
        val_acc = 100. * correct / total
        
        return val_loss, val_acc
    
    def train(self, epochs):
        """
        Train model for multiple epochs.
        
        Args:
            epochs: Number of epochs to train
        """
        best_val_acc = 0.0
        
        with mlflow.start_run():
            # Log hyperparameters
            mlflow.log_params(self.config)
            
            for epoch in range(epochs):
                logger.info(f"\\nEpoch {epoch+1}/{epochs}")
                
                # Train
                train_loss, train_acc = self.train_epoch()
                
                # Validate
                val_loss, val_acc = self.validate()
                
                # Update scheduler
                if self.scheduler:
                    if isinstance(self.scheduler, optim.lr_scheduler.ReduceLROnPlateau):
                        self.scheduler.step(val_loss)
                    else:
                        self.scheduler.step()
                
                # Log metrics
                mlflow.log_metrics({
                    'train_loss': train_loss,
                    'train_acc': train_acc,
                    'val_loss': val_loss,
                    'val_acc': val_acc,
                    'learning_rate': self.optimizer.param_groups[0]['lr']
                }, step=epoch)
                
                self.train_losses.append(train_loss)
                self.val_losses.append(val_loss)
                self.val_accuracies.append(val_acc)
                
                logger.info(f"Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.2f}%")
                logger.info(f"Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.2f}%")
                
                # Save best model
                if val_acc > best_val_acc:
                    best_val_acc = val_acc
                    self.save_checkpoint('best_model.pth', epoch)
                    logger.info(f"✅ New best model saved! Val Acc: {val_acc:.2f}%")
                
                # Save checkpoint
                if (epoch + 1) % self.config.get('checkpoint_freq', 10) == 0:
                    self.save_checkpoint(f'checkpoint_epoch_{epoch+1}.pth', epoch)
            
            logger.info(f"\\n✅ Training complete! Best Val Acc: {best_val_acc:.2f}%")
    
    def save_checkpoint(self, filename, epoch):
        """Save training checkpoint."""
        checkpoint_dir = Path('checkpoints')
        checkpoint_dir.mkdir(exist_ok=True)
        
        filepath = checkpoint_dir / filename
        
        self.model.save_checkpoint(
            filepath,
            epoch,
            self.optimizer,
            self.train_losses[-1] if self.train_losses else 0
        )

# Usage
config = {
    'loss': 'cross_entropy',
    'optimizer': 'adam',
    'learning_rate': 0.001,
    'scheduler': 'cosine',
    'epochs': 50,
    'checkpoint_freq': 10,
    'experiment_name': 'cnn_training'
}

trainer = Trainer(model, train_loader, val_loader, config)
trainer.train(epochs=50)
```

**Verification:**
- [ ] Training loop working
- [ ] Validation running
- [ ] Checkpoints saving
- [ ] Metrics logged
- [ ] Best model saved

**If This Fails:**
→ Check data loaders
→ Verify loss function
→ Review optimizer settings
→ Test with small dataset
→ Check GPU memory

---

### Step 3: Implement TensorFlow/Keras Models

**What:** Build equivalent models using TensorFlow/Keras

**How:**

**TensorFlow Model:**
```python
# models/tf_cnn.py
"""
TensorFlow/Keras CNN implementation
"""

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models
import numpy as np

class TensorFlowCNN:
    """CNN using TensorFlow/Keras."""
    
    def __init__(self, num_classes=10, input_shape=(32, 32, 3)):
        """
        Initialize CNN.
        
        Args:
            num_classes: Number of output classes
            input_shape: Input image shape
        """
        self.num_classes = num_classes
        self.input_shape = input_shape
        self.model = self._build_model()
    
    def _build_model(self):
        """Build CNN architecture."""
        model = models.Sequential([
            # Conv block 1
            layers.Conv2D(32, (3, 3), padding='same', input_shape=self.input_shape),
            layers.BatchNormalization(),
            layers.Activation('relu'),
            layers.MaxPooling2D((2, 2)),
            
            # Conv block 2
            layers.Conv2D(64, (3, 3), padding='same'),
            layers.BatchNormalization(),
            layers.Activation('relu'),
            layers.MaxPooling2D((2, 2)),
            
            # Conv block 3
            layers.Conv2D(128, (3, 3), padding='same'),
            layers.BatchNormalization(),
            layers.Activation('relu'),
            layers.MaxPooling2D((2, 2)),
            
            # Fully connected
            layers.Flatten(),
            layers.Dense(512, activation='relu'),
            layers.Dropout(0.5),
            layers.Dense(self.num_classes, activation='softmax')
        ])
        
        return model
    
    def compile_model(self, learning_rate=0.001):
        """Compile model."""
        self.model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=learning_rate),
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
    
    def train(self, train_data, val_data, epochs=50, batch_size=32):
        """
        Train model.
        
        Args:
            train_data: Tuple of (X_train, y_train)
            val_data: Tuple of (X_val, y_val)
            epochs: Number of epochs
            batch_size: Batch size
        """
        X_train, y_train = train_data
        X_val, y_val = val_data
        
        # Callbacks
        callbacks = [
            keras.callbacks.ModelCheckpoint(
                'best_model.h5',
                save_best_only=True,
                monitor='val_accuracy'
            ),
            keras.callbacks.EarlyStopping(
                monitor='val_loss',
                patience=10,
                restore_best_weights=True
            ),
            keras.callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=5,
                min_lr=1e-7
            ),
            keras.callbacks.TensorBoard(
                log_dir='logs',
                histogram_freq=1
            )
        ]
        
        # Train
        history = self.model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callbacks,
            verbose=1
        )
        
        return history
    
    def evaluate(self, X_test, y_test):
        """Evaluate model."""
        loss, accuracy = self.model.evaluate(X_test, y_test, verbose=0)
        print(f"Test Loss: {loss:.4f}")
        print(f"Test Accuracy: {accuracy:.4f}")
        return loss, accuracy
    
    def predict(self, X):
        """Make predictions."""
        return self.model.predict(X)
    
    def save(self, filepath):
        """Save model."""
        self.model.save(filepath)
        print(f"✅ Model saved to {filepath}")
    
    def load(self, filepath):
        """Load model."""
        self.model = keras.models.load_model(filepath)
        print(f"✅ Model loaded from {filepath}")

# Usage
tf_model = TensorFlowCNN(num_classes=10)
tf_model.compile_model(learning_rate=0.001)

history = tf_model.train(
    (X_train, y_train),
    (X_val, y_val),
    epochs=50,
    batch_size=32
)

tf_model.evaluate(X_test, y_test)
tf_model.save('models/tf_cnn_model.h5')
```

**Transformer Architecture (PyTorch):**
```python
# models/transformer.py
"""
Transformer architecture for NLP
"""

import torch
import torch.nn as nn
import math

class PositionalEncoding(nn.Module):
    """Positional encoding for transformer."""
    
    def __init__(self, d_model, max_len=5000):
        super(PositionalEncoding, self).__init__()
        
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * 
                            (-math.log(10000.0) / d_model))
        
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        
        pe = pe.unsqueeze(0)
        self.register_buffer('pe', pe)
    
    def forward(self, x):
        return x + self.pe[:, :x.size(1), :]

class TransformerModel(BaseModel):
    """Transformer for sequence tasks."""
    
    def __init__(self, vocab_size, d_model=512, nhead=8, 
                 num_layers=6, dim_feedforward=2048, max_seq_length=512):
        super(TransformerModel, self).__init__()
        
        self.d_model = d_model
        
        # Embeddings
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.pos_encoder = PositionalEncoding(d_model, max_seq_length)
        
        # Transformer encoder
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=dim_feedforward,
            dropout=0.1
        )
        self.transformer_encoder = nn.TransformerEncoder(encoder_layer, num_layers)
        
        # Output layer
        self.fc = nn.Linear(d_model, vocab_size)
        
        self._init_weights()
    
    def _init_weights(self):
        """Initialize weights."""
        initrange = 0.1
        self.embedding.weight.data.uniform_(-initrange, initrange)
        self.fc.bias.data.zero_()
        self.fc.weight.data.uniform_(-initrange, initrange)
    
    def forward(self, src, src_mask=None):
        """
        Forward pass.
        
        Args:
            src: Source sequence (batch_size, seq_len)
            src_mask: Source mask
            
        Returns:
            Output predictions
        """
        # Embedding + positional encoding
        src = self.embedding(src) * math.sqrt(self.d_model)
        src = self.pos_encoder(src)
        
        # Transformer encoding
        output = self.transformer_encoder(src, src_mask)
        
        # Output projection
        output = self.fc(output)
        
        return output
```

**Verification:**
- [ ] TensorFlow model working
- [ ] Keras API functional
- [ ] Transformer implemented
- [ ] Training callbacks active
- [ ] Models saving correctly

**If This Fails:**
→ Check TensorFlow version
→ Verify input shapes
→ Review model architecture
→ Test callbacks
→ Check GPU memory

---

### Step 4: Implement Transfer Learning

**What:** Use pre-trained models for transfer learning

**How:**

**PyTorch Transfer Learning:**
```python
# src/models/transfer_learning.py
"""
Transfer learning with pre-trained models
"""

import torch
import torch.nn as nn
import torchvision.models as models

class TransferLearningModel:
    """Transfer learning wrapper."""
    
    def __init__(self, model_name='resnet50', num_classes=10, freeze_backbone=True):
        """
        Initialize transfer learning model.
        
        Args:
            model_name: Pre-trained model name
            num_classes: Number of output classes
            freeze_backbone: Whether to freeze pre-trained layers
        """
        self.model_name = model_name
        self.num_classes = num_classes
        self.model = self._load_pretrained_model(freeze_backbone)
    
    def _load_pretrained_model(self, freeze_backbone):
        """Load and modify pre-trained model."""
        
        if self.model_name == 'resnet50':
            model = models.resnet50(pretrained=True)
            
            # Freeze backbone
            if freeze_backbone:
                for param in model.parameters():
                    param.requires_grad = False
            
            # Replace final layer
            num_features = model.fc.in_features
            model.fc = nn.Sequential(
                nn.Linear(num_features, 512),
                nn.ReLU(),
                nn.Dropout(0.5),
                nn.Linear(512, self.num_classes)
            )
        
        elif self.model_name == 'efficientnet_b0':
            model = models.efficientnet_b0(pretrained=True)
            
            if freeze_backbone:
                for param in model.parameters():
                    param.requires_grad = False
            
            num_features = model.classifier[1].in_features
            model.classifier = nn.Sequential(
                nn.Dropout(0.5),
                nn.Linear(num_features, self.num_classes)
            )
        
        elif self.model_name == 'vit_b_16':
            model = models.vit_b_16(pretrained=True)
            
            if freeze_backbone:
                for param in model.parameters():
                    param.requires_grad = False
            
            num_features = model.heads.head.in_features
            model.heads.head = nn.Linear(num_features, self.num_classes)
        
        else:
            raise ValueError(f"Unknown model: {self.model_name}")
        
        return model
    
    def unfreeze_layers(self, num_layers=None):
        """
        Unfreeze layers for fine-tuning.
        
        Args:
            num_layers: Number of layers to unfreeze from the end (None = all)
        """
        if num_layers is None:
            # Unfreeze all layers
            for param in self.model.parameters():
                param.requires_grad = True
        else:
            # Unfreeze specific number of layers
            layers = list(self.model.children())
            for layer in layers[-num_layers:]:
                for param in layer.parameters():
                    param.requires_grad = True
        
        print(f"✅ Unfroze layers for fine-tuning")

# Usage - PyTorch
transfer_model = TransferLearningModel('resnet50', num_classes=10, freeze_backbone=True)

# Train with frozen backbone
trainer = Trainer(transfer_model.model, train_loader, val_loader, config)
trainer.train(epochs=10)

# Unfreeze and fine-tune
transfer_model.unfreeze_layers(num_layers=3)
config['learning_rate'] = 0.0001  # Lower learning rate for fine-tuning
trainer = Trainer(transfer_model.model, train_loader, val_loader, config)
trainer.train(epochs=20)
```

**TensorFlow Transfer Learning:**
```python
# src/models/tf_transfer.py
"""
TensorFlow transfer learning
"""

import tensorflow as tf
from tensorflow.keras.applications import (
    ResNet50, EfficientNetB0, VGG16, MobileNetV2
)
from tensorflow.keras import layers, models

class TFTransferLearning:
    """TensorFlow transfer learning."""
    
    def __init__(self, model_name='ResNet50', num_classes=10, 
                 input_shape=(224, 224, 3), freeze_backbone=True):
        self.model_name = model_name
        self.num_classes = num_classes
        self.input_shape = input_shape
        self.model = self._build_model(freeze_backbone)
    
    def _build_model(self, freeze_backbone):
        """Build transfer learning model."""
        
        # Load pre-trained base model
        if self.model_name == 'ResNet50':
            base_model = ResNet50(weights='imagenet', include_top=False, 
                                 input_shape=self.input_shape)
        elif self.model_name == 'EfficientNetB0':
            base_model = EfficientNetB0(weights='imagenet', include_top=False,
                                       input_shape=self.input_shape)
        elif self.model_name == 'VGG16':
            base_model = VGG16(weights='imagenet', include_top=False,
                              input_shape=self.input_shape)
        else:
            raise ValueError(f"Unknown model: {self.model_name}")
        
        # Freeze base model
        base_model.trainable = not freeze_backbone
        
        # Build complete model
        model = models.Sequential([
            base_model,
            layers.GlobalAveragePooling2D(),
            layers.Dense(512, activation='relu'),
            layers.Dropout(0.5),
            layers.Dense(self.num_classes, activation='softmax')
        ])
        
        return model
    
    def compile(self, learning_rate=0.001):
        """Compile model."""
        self.model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate),
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
    
    def unfreeze_for_finetuning(self, num_layers=None):
        """Unfreeze layers for fine-tuning."""
        base_model = self.model.layers[0]
        base_model.trainable = True
        
        if num_layers is not None:
            # Freeze all layers except last num_layers
            for layer in base_model.layers[:-num_layers]:
                layer.trainable = False
        
        # Recompile with lower learning rate
        self.compile(learning_rate=0.0001)
        
        print(f"✅ Model unfrozen for fine-tuning")

# Usage - TensorFlow
tf_transfer = TFTransferLearning('ResNet50', num_classes=10)
tf_transfer.compile(learning_rate=0.001)

# Train
history = tf_transfer.model.fit(
    train_dataset,
    validation_data=val_dataset,
    epochs=10
)

# Fine-tune
tf_transfer.unfreeze_for_finetuning(num_layers=20)
history_finetune = tf_transfer.model.fit(
    train_dataset,
    validation_data=val_dataset,
    epochs=20
)
```

**Verification:**
- [ ] Pre-trained models loaded
- [ ] Layers frozen correctly
- [ ] Fine-tuning working
- [ ] Transfer learning effective
- [ ] Performance improved

**If This Fails:**
→ Check model availability
→ Verify input shapes
→ Review freezing logic
→ Test with simple model
→ Check learning rates

---

### Step 5: Model Optimization and Deployment

**What:** Optimize models for production deployment

**How:**

**Model Quantization (PyTorch):**
```python
# src/optimization/quantization.py
"""
Model quantization for deployment
"""

import torch
import torch.quantization

def quantize_model(model, calibration_loader):
    """
    Quantize model for faster inference.
    
    Args:
        model: PyTorch model
        calibration_loader: Data loader for calibration
        
    Returns:
        Quantized model
    """
    # Set to evaluation mode
    model.eval()
    
    # Fuse layers
    model_fused = torch.quantization.fuse_modules(
        model,
        [['conv', 'bn', 'relu']]  # Adjust based on your model
    )
    
    # Prepare for quantization
    model_fused.qconfig = torch.quantization.get_default_qconfig('fbgemm')
    model_prepared = torch.quantization.prepare(model_fused)
    
    # Calibrate
    with torch.no_grad():
        for data, _ in calibration_loader:
            model_prepared(data)
    
    # Convert to quantized model
    model_quantized = torch.quantization.convert(model_prepared)
    
    print("✅ Model quantized")
    
    return model_quantized

# Model pruning
def prune_model(model, amount=0.3):
    """Prune model to reduce size."""
    import torch.nn.utils.prune as prune
    
    for name, module in model.named_modules():
        if isinstance(module, torch.nn.Conv2d):
            prune.l1_unstructured(module, name='weight', amount=amount)
        elif isinstance(module, torch.nn.Linear):
            prune.l1_unstructured(module, name='weight', amount=amount)
    
    print(f"✅ Model pruned ({amount*100}% of weights)")
    
    return model
```

**ONNX Export:**
```python
# src/deployment/onnx_export.py
"""
Export model to ONNX format
"""

import torch
import onnx
import onnxruntime

def export_to_onnx(model, dummy_input, output_path):
    """
    Export PyTorch model to ONNX.
    
    Args:
        model: PyTorch model
        dummy_input: Example input tensor
        output_path: Path to save ONNX model
    """
    model.eval()
    
    torch.onnx.export(
        model,
        dummy_input,
        output_path,
        export_params=True,
        opset_version=11,
        do_constant_folding=True,
        input_names=['input'],
        output_names=['output'],
        dynamic_axes={
            'input': {0: 'batch_size'},
            'output': {0: 'batch_size'}
        }
    )
    
    # Verify
    onnx_model = onnx.load(output_path)
    onnx.checker.check_model(onnx_model)
    
    print(f"✅ Model exported to {output_path}")

# Usage
dummy_input = torch.randn(1, 3, 224, 224)
export_to_onnx(model, dummy_input, 'model.onnx')

# ONNX Runtime inference
ort_session = onnxruntime.InferenceSession('model.onnx')
ort_inputs = {ort_session.get_inputs()[0].name: dummy_input.numpy()}
ort_outputs = ort_session.run(None, ort_inputs)
```

**Verification:**
- [ ] Model quantized
- [ ] Pruning working
- [ ] ONNX export successful
- [ ] Inference faster
- [ ] Accuracy maintained

**If This Fails:**
→ Check quantization support
→ Verify layer compatibility
→ Review ONNX version
→ Test with simple model
→ Check accuracy degradation

---

## Verification Checklist

After completing this workflow:

- [ ] PyTorch environment set up
- [ ] TensorFlow installed
- [ ] Models implemented
- [ ] Training loops working
- [ ] Transfer learning functional
- [ ] Models optimized
- [ ] ONNX export successful
- [ ] Documentation complete

---

## Best Practices

### DO:
✅ Use GPU for training
✅ Implement data augmentation
✅ Use batch normalization
✅ Add dropout for regularization
✅ Monitor training metrics
✅ Save checkpoints regularly
✅ Use transfer learning
✅ Implement early stopping
✅ Validate on separate data
✅ Use learning rate scheduling
✅ Track experiments with MLflow
✅ Optimize for deployment

### DON'T:
❌ Train without validation
❌ Ignore overfitting
❌ Use too large batch size
❌ Skip data preprocessing
❌ Forget to normalize inputs
❌ Use random initialization only
❌ Train from scratch unnecessarily
❌ Ignore GPU memory limits
❌ Skip hyperparameter tuning
❌ Deploy without optimization
❌ Forget to test inference speed
❌ Ignore model size

---

## Related Workflows

**Prerequisites:**
- [data_preprocessing_pipelines.md](./data_preprocessing_pipelines.md) - Preprocessing
- [ml_experiment_setup.md](./ml_experiment_setup.md) - Experiments

**Next Steps:**
- [model_deployment_strategies.md](./model_deployment_strategies.md) - Deployment
- [model_monitoring_observability.md](./model_monitoring_observability.md) - Monitoring

**Related:**
- [automl_hyperparameter_optimization.md](./automl_hyperparameter_optimization.md) - Optimization

---

## Tags
`deep-learning` `pytorch` `tensorflow` `cnn` `rnn` `transformer` `transfer-learning` `neural-networks` `gpu` `optimization`
