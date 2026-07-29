# Attention Is All You Need: Transformer Architectural Deep Dive

## Abstract
The Transformer architecture relies entirely on self-attention mechanisms to compute representations of its input and output without using sequence-aligned RNNs or convolution.

## Scaled Dot-Product Attention
Attention is computed as:
$$Attention(Q, K, V) = softmax\left(\frac{QK^T}{\sqrt{d_k}}\right)V$$

Where $Q$ is the Query matrix, $K$ is the Key matrix, and $V$ is the Value matrix.

## Multi-Head Self-Attention
Multi-head attention allows the model to jointly attend to information from different representation subspaces at different positions.
