CHARSET = sorted(set("inm""仲夏夜银梦""インム""哼哼哼啊啊啊啊啊""114514""いいよ、こいよ""1919""イクイク""810""野獣先輩""野兽先辈""889464""はやくしろよ""931""臭い""ホモ""行き過ぎイク、イクイク""你是一个一个一个""rape""レイプ""雷普""そうだよ""三回啊三回""やりますね""压力马斯内""会员制餐厅""下北沢""食雪汉""ちしょう""池沼""林檎""（悲""（喜""（恼""田所浩二""先輩！好きッス！""俺もお前がすきだ。""先輩お菓子ですか？""好きにしろ！""屑""鉴""撅"))

CHARSET_LENGTH = len(CHARSET)
assert CHARSET_LENGTH == 114, "あぁぁぁぁぁぁぁぁぁぁぁぁぁ！！！"


def encode(content: bytes) -> str:
    num = int.from_bytes(content, byteorder="big")
    encoded = ""

    while num:
        encoded = CHARSET[num % CHARSET_LENGTH] + encoded
        num //= CHARSET_LENGTH

    return encoded
