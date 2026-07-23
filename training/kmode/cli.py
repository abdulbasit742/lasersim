import argparse


def build_parser():
    parser = argparse.ArgumentParser(description='LaserSim K-mode training tools')
    parser.add_argument('--mode', choices=['train', 'predict'], default='train')
    parser.add_argument('--epochs', type=int, default=10)
    return parser


if __name__ == '__main__':
    args = build_parser().parse_args()
    print(f'Running {args.mode} for {args.epochs} epochs')
