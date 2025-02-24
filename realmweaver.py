# This will be the main entry point (will handle world generation) This line at the top will remind me what each .py file is for so please do not remove!

import argparse
from world_generator import generate_world
from visualization import visualize_world

def main():
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description='Generate and visualize procedural worlds')
    parser.add_argument('--size', type=int, default=50, help='Size of the world (default: 50)')
    parser.add_argument('--seed', type=int, help='Seed for world generation (optional)')
    parser.add_argument('--save', type=str, help='Save the map to specified image file')
    parser.add_argument('--show', action='store_true', help='Show the map in a window')
    args = parser.parse_args()

    # Generate world with optional seed
    world, used_seed = generate_world(size=args.size, seed=args.seed)
    
    # Visualize/save based on arguments
    visualize_world(world, used_seed, save_path=args.save, show=args.show)
    
    # Print information about the generation
    print(f"World generated with seed: {used_seed}")
    if args.save:
        print(f"Map saved to: {args.save}")

if __name__ == "__main__":
    main()
