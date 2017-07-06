import torch

x = torch.ones(3)
y = torch.ones(3)

if torch.cuda.is_available():
    print("Using CUDA")
    x = x.cuda()
    y = y.cuda()
else:
    print("CUDA is not available")

print(x + y)