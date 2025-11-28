from base114_encode import encode as base114_encode
from itertools import cycle

ENCODED_FLAG = "プ斯前i是臭三、に压田ク会田员ね内し悲に哼厅撅池食三でそ好辈m俺二、ぎ压で所！そ沢三林喜ス哼檎马"

KEY = [1, 1, 4, 5, 1, 4, 1, 9, 1, 9, 8, 1, 0]


def main() -> None:
    user_input = input("请输入你的 Flag（对了有奖励，错了有惩罚哦～）: ").encode()
    encrypted = bytes(ch ^ key for ch, key in zip(user_input, cycle(KEY)))
    encoded = base114_encode(encrypted)

    if encoded == ENCODED_FLAG:
        print("对了，奖励你去会员制餐厅吃一顿（喜")
    else:
        print("这 Flag 不对啊，你被雷普了（悲")


if __name__ == "__main__":
    main()
