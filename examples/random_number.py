import random

def get_random_number(min_val=1, max_val=100):
    """生成指定范围内的随机数"""
    return random.randint(min_val, max_val)

def main():
    number = get_random_number()
    print(f"生成的随机数是: {number}")

if __name__ == "__main__":
    main()
