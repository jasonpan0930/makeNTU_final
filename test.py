import torch

# Check if CUDA (GPU) is available
if torch.cuda.is_available():
    # Get the current GPU device
    device = torch.cuda.current_device()
    gpu_name = torch.cuda.get_device_name(device)
    vram_total = torch.cuda.get_device_properties(device).total_memory / (1024 ** 3)  # Convert to GB
    vram_used = torch.cuda.memory_allocated(device) / (1024 ** 3)
    vram_free = vram_total - vram_used

    print(f"GPU: {gpu_name}")
    print(f"Total VRAM: {vram_total:.2f} GB")
    print(f"Used VRAM: {vram_used:.2f} GB")
    print(f"Free VRAM: {vram_free:.2f} GB")
else:
    print("CUDA (GPU) is not available. Using CPU.")