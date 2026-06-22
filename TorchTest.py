import torch

print(torch.backends.mps.is_available())
print(torch.__version__)
print(torch.rand(3,3))
