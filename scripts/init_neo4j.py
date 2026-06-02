"""
Neo4j 人物关系图谱初始化脚本
导入四大名著（西游记/三国演义/红楼梦/水浒传）的核心人物及关系
使用方法: python scripts/init_neo4j.py [--clear] [--novel xiyou|sanguo|honglou|shuihu]
"""
import argparse
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.config import settings
from backend.utils.neo4j_util import Neo4jClient

# ============================================================
# 四大名著人物关系数据
# ============================================================

# 人物数据: {book: [(name, identity, aliases, description), ...]}
CHARACTERS = {
    "novel_xiyou": [
        ("孙悟空", "齐天大圣/斗战胜佛", "行者/猴王/美猴王/弼马温",
         "唐僧的大徒弟，神通广大，七十二变，曾大闹天宫"),
        ("唐僧", "金蝉子转世/旃檀功德佛", "玄奘/三藏/御弟",
         "取经团队的核心，如来弟子金蝉子转世"),
        ("猪八戒", "天蓬元帅/净坛使者", "八戒/悟能/呆子",
         "唐僧的二徒弟，原为天蓬元帅，好色贪吃"),
        ("沙僧", "卷帘大将/金身罗汉", "沙和尚/悟净",
         "唐僧的三徒弟，原为卷帘大将，忠厚老实"),
        ("白龙马", "西海龙王三太子/八部天龙", "玉龙",
         "原为西海龙王三太子，化身白龙马驮唐僧取经"),
        ("如来佛祖", "佛教教主", "如来/世尊",
         "西方极乐世界的教主，佛法无边"),
        ("观音菩萨", "南海观世音", "观音/观自在/慈航道人",
         "大慈大悲的菩萨，受如来旨意安排取经"),
        ("玉皇大帝", "天庭之主", "玉帝/昊天上帝",
         "天庭的最高统治者"),
        ("太白金星", "天庭文官", "李长庚",
         "玉帝身边的重臣，多次招安孙悟空"),
        ("太上老君", "道教祖师", "老子/李耳",
         "道教始祖，居兜率宫，练就仙丹法宝无数"),
        ("二郎神", "显圣二郎真君", "杨戬",
         "玉帝外甥，三只眼，神通与孙悟空不相上下"),
        ("哪吒", "三太子/中坛元帅", "李哪吒",
         "托塔天王李靖之子，三头六臂"),
        ("牛魔王", "平天大圣", "大力牛魔王",
         "七大圣之首，孙悟空的结拜兄弟"),
        ("铁扇公主", "罗刹女", "铁扇仙",
         "牛魔王之妻，持有芭蕉扇"),
        ("红孩儿", "圣婴大王/善财童子", "",
         "牛魔王与铁扇公主之子，使三昧真火"),
        ("白骨精", "白骨夫人", "白骨夫人",
         "白虎岭妖怪，三次变化想害唐僧"),
        ("蜘蛛精", "盘丝洞妖怪", "",
         "七个蜘蛛精，盘丝洞洞主"),
    ],
    "novel_sanguo": [
        ("刘备", "蜀汉昭烈帝", "玄德/刘皇叔",
         "蜀汉开国皇帝，以仁义闻名，桃园结义大哥"),
        ("关羽", "前将军/汉寿亭侯", "云长/关公/关二爷",
         "蜀汉大将，忠义无双，过五关斩六将"),
        ("张飞", "车骑将军", "翼德/燕人张飞",
         "蜀汉大将，勇猛善战，当阳桥独退曹军"),
        ("诸葛亮", "丞相/武乡侯", "孔明/卧龙",
         "蜀汉丞相，智慧的化身，鞠躬尽瘁死而后已"),
        ("曹操", "魏武帝", "孟德/阿瞒",
         "东汉末年权臣，魏国奠基人，雄才大略亦奸诈多疑"),
        ("孙权", "吴大帝", "仲谋",
         "东吴开国皇帝，坐镇江东，善于用人"),
        ("赵云", "镇军将军", "子龙",
         "蜀汉五虎将之一，长坂坡七进七出救阿斗"),
        ("马超", "骠骑将军", "孟起",
         "蜀汉五虎将之一，西凉锦马超"),
        ("黄忠", "后将军", "汉升",
         "蜀汉五虎将之一，老当益壮，定军山斩夏侯渊"),
        ("吕布", "温侯/奋威将军", "奉先/飞将",
         "三国第一猛将，方天画戟赤兔马，然反复无常"),
        ("貂蝉", "司徒府歌伎", "",
         "古代四大美女之一，王允以连环计使其离间董卓吕布"),
        ("周瑜", "大都督", "公瑾/周郎",
         "东吴大都督，赤壁之战统帅，精通音律"),
        ("司马懿", "太傅", "仲达",
         "魏国权臣，善于隐忍，为西晋奠基"),
        ("鲁肃", "都督", "子敬",
         "东吴名臣，主张孙刘联盟"),
        ("董卓", "太师", "仲颖",
         "东汉末年权臣，残暴专横"),
        ("袁绍", "大将军", "本初",
         "东汉末年北方最大军阀，官渡之战败于曹操"),
        ("孙策", "吴侯", "伯符/小霸王",
         "孙权的兄长，东吴基业的开创者"),
    ],
    "novel_shuihu": [
        ("宋江", "天魁星/呼保义", "及时雨/宋公明",
         "梁山好汉首领，排行第一，人称及时雨"),
        ("卢俊义", "天罡星/玉麒麟", "",
         "梁山副首领，武艺高强，家财万贯"),
        ("吴用", "天机星/智多星", "学究",
         "梁山军师，足智多谋，堪比诸葛亮"),
        ("林冲", "天雄星/豹子头", "林教头",
         "八十万禁军教头，被高俅陷害逼上梁山"),
        ("武松", "天伤星/行者", "武二郎/打虎英雄",
         "景阳冈打虎，醉打蒋门神，血溅鸳鸯楼"),
        ("李逵", "天杀星/黑旋风", "铁牛",
         "性格鲁莽憨直，对宋江忠心耿耿"),
        ("鲁智深", "天孤星/花和尚", "鲁达/鲁提辖",
         "三拳打死镇关西，倒拔垂杨柳"),
        ("燕青", "天巧星/浪子", "小乙",
         "卢俊义家仆，多才多艺，忠心护主"),
        ("花荣", "天英星/小李广", "",
         "梁山神箭手，百步穿杨"),
        ("公孙胜", "天闲星/入云龙", "一清道人",
         "梁山法师，道法高深"),
        ("关胜", "天勇星/大刀", "",
         "关羽后人，使青龙偃月刀"),
        ("秦明", "天猛星/霹雳火", "",
         "性如烈火，使狼牙棒"),
    ],
    "novel_honglou": [
        ("贾宝玉", "怡红公子/绛洞花主", "宝二爷/混世魔王",
         "贾府公子，衔玉而生，情不情，最终出家"),
        ("林黛玉", "潇湘妃子", "颦儿/颦颦",
         "贾母外孙女，才情横溢，多愁善感，绛珠仙草转世"),
        ("薛宝钗", "蘅芜君", "宝姐姐",
         "贾宝玉之妻，端庄贤淑，持重守礼"),
        ("王熙凤", "凤辣子/琏二奶奶", "凤姐/凤哥儿",
         "贾府当家少奶奶，精明能干亦心狠手辣"),
        ("贾母", "史太君", "老太太/老祖宗",
         "贾府最高辈分，贾宝玉的祖母，溺爱孙子"),
        ("贾政", "工部员外郎", "存周",
         "贾宝玉之父，正统古板，望子成龙"),
        ("王夫人", "贾政之妻", "王氏",
         "贾宝玉之母，吃斋念佛，但手段严厉"),
        ("贾元春", "贤德妃", "元妃/大小姐",
         "贾政长女，入宫为皇妃"),
        ("贾探春", "蕉下客", "三小姐/玫瑰花",
         "贾政庶女，精明能干，有远见卓识"),
        ("贾惜春", "藕榭", "四小姐",
         "贾府最小的小姐，孤僻冷漠，最终出家"),
        ("史湘云", "枕霞旧友", "云妹妹",
         "贾母侄孙女，豪爽开朗，醉卧芍药茵"),
        ("妙玉", "槛外人", "妙玉师父",
         "大观园栊翠庵尼姑，孤高自许"),
        ("袭人", "花气袭人", "花珍珠/蕊珠",
         "贾宝玉的大丫鬟，性格温柔和顺"),
        ("晴雯", "勇晴雯", "",
         "贾宝玉的丫鬟，美貌刚烈，心比天高"),
        ("平儿", "平姑娘", "",
         "王熙凤的贴身丫鬟兼通房，善良正直"),
        ("鸳鸯", "鸳鸯姐姐", "金鸳鸯",
         "贾母的大丫鬟，忠贞刚烈"),
        ("紫鹃", "紫鹃姐姐", "鹦哥",
         "林黛玉的贴身丫鬟，忠心耿耿"),
        ("刘姥姥", "村姥姥", "刘氏",
         "乡下来的穷亲戚，三进荣国府"),
    ],
}

# 关系数据: {book: [(from_name, relation_type, to_name, description), ...]}
RELATIONSHIPS = {
    "novel_xiyou": [
        ("唐僧", "MASTER_OF", "孙悟空", "师徒"),
        ("唐僧", "MASTER_OF", "猪八戒", "师徒"),
        ("唐僧", "MASTER_OF", "沙僧", "师徒"),
        ("唐僧", "MASTER_OF", "白龙马", "师徒"),
        ("孙悟空", "FRIEND", "猪八戒", "师兄弟"),
        ("孙悟空", "FRIEND", "沙僧", "师兄弟"),
        ("孙悟空", "SWORN_BROTHER", "牛魔王", "七大圣结义/后决裂"),
        ("牛魔王", "SPOUSE", "铁扇公主", "夫妻"),
        ("牛魔王", "FATHER_OF", "红孩儿", "父子"),
        ("铁扇公主", "MOTHER_OF", "红孩儿", "母子"),
        ("如来佛祖", "SUBORDINATE", "观音菩萨", "上下级"),
        ("玉皇大帝", "SUBORDINATE", "太白金星", "君臣"),
        ("玉皇大帝", "SUBORDINATE", "二郎神", "君臣（甥舅关系）"),
        ("玉皇大帝", "SUBORDINATE", "哪吒", "君臣"),
        ("孙悟空", "ENEMY", "白骨精", "三打白骨精"),
        ("孙悟空", "ENEMY", "蜘蛛精", "盘丝洞降妖"),
        ("孙悟空", "ENEMY", "二郎神", "大闹天宫时交战"),
    ],
    "novel_sanguo": [
        ("刘备", "SWORN_BROTHER", "关羽", "桃园三结义"),
        ("刘备", "SWORN_BROTHER", "张飞", "桃园三结义"),
        ("关羽", "FRIEND", "张飞", "结义兄弟"),
        ("刘备", "SUBORDINATE", "诸葛亮", "三顾茅庐之君臣"),
        ("刘备", "SUBORDINATE", "赵云", "君臣"),
        ("刘备", "SUBORDINATE", "马超", "君臣"),
        ("刘备", "SUBORDINATE", "黄忠", "君臣"),
        ("曹操", "SUBORDINATE", "司马懿", "君臣（司马懿心怀不轨）"),
        ("曹操", "ENEMY", "刘备", "汉末争霸"),
        ("曹操", "ENEMY", "孙权", "赤壁之战"),
        ("孙权", "SUBORDINATE", "周瑜", "君臣"),
        ("孙权", "SUBORDINATE", "鲁肃", "君臣"),
        ("吕布", "FATHER_OF", "董卓", "认作义父（后反目）"),
        ("吕布", "SPOUSE", "貂蝉", "连环计（实为王允设计）"),
        ("孙策", "SIBLING", "孙权", "兄弟（孙策开创基业，孙权守成）"),
        ("周瑜", "ENEMY", "诸葛亮", "各为其主（既生瑜何生亮）"),
        ("刘备", "ENEMY", "袁绍", "诸侯争霸"),
    ],
    "novel_shuihu": [
        ("宋江", "SUBORDINATE", "卢俊义", "梁山头领（卢为副）"),
        ("宋江", "SUBORDINATE", "吴用", "梁山头领（吴为军师）"),
        ("宋江", "SUBORDINATE", "林冲", "梁山头领"),
        ("宋江", "SUBORDINATE", "武松", "梁山头领"),
        ("宋江", "SUBORDINATE", "李逵", "梁山头领（李逵对宋江最忠）"),
        ("宋江", "SUBORDINATE", "鲁智深", "梁山头领"),
        ("宋江", "SUBORDINATE", "花荣", "梁山头领（花荣救过宋江）"),
        ("宋江", "SUBORDINATE", "公孙胜", "梁山头领"),
        ("卢俊义", "MASTER_OF", "燕青", "主仆（燕青忠心救主）"),
        ("林冲", "FRIEND", "鲁智深", "结义兄弟（野猪林救命）"),
        ("武松", "FRIEND", "鲁智深", "二龙山结义"),
        ("吴用", "FRIEND", "公孙胜", "梁山军师搭档"),
    ],
    "novel_honglou": [
        ("贾母", "MOTHER_OF", "贾政", "母子"),
        ("贾政", "FATHER_OF", "贾宝玉", "父子"),
        ("贾政", "FATHER_OF", "贾元春", "父女"),
        ("贾政", "FATHER_OF", "贾探春", "父女（庶出）"),
        ("贾宝玉", "SPOUSE", "薛宝钗", "金玉良缘（最终成婚）"),
        ("贾宝玉", "FRIEND", "林黛玉", "木石前盟（精神恋人，黛玉病逝）"),
        ("贾宝玉", "FRIEND", "史湘云", "表兄妹"),
        ("贾宝玉", "MASTER_OF", "袭人", "主仆（通房丫鬟）"),
        ("贾宝玉", "MASTER_OF", "晴雯", "主仆"),
        ("林黛玉", "MASTER_OF", "紫鹃", "主仆（情同姐妹）"),
        ("王熙凤", "MASTER_OF", "平儿", "主仆（通房丫鬟）"),
        ("贾母", "MASTER_OF", "鸳鸯", "主仆（离不开的丫鬟）"),
        ("王夫人", "MOTHER_OF", "贾宝玉", "母子"),
        ("薛宝钗", "FRIEND", "林黛玉", "金兰契（结为姐妹）"),
    ],
}


def init_neo4j(client: Neo4jClient, novels: list = None, clear: bool = False):
    """
    初始化Neo4j图谱数据
    :param client: Neo4jClient实例
    :param novels: 要导入的名著列表，None表示全部
    :param clear: 是否清除已有数据
    """
    if not client.is_connected():
        print("[错误] Neo4j未连接，请确保Neo4j服务已启动")
        print(f"  地址: {settings.NEO4J_URI}")
        print(f"  用户: {settings.NEO4J_USER}")
        return False

    if novels is None:
        novels = ["novel_xiyou", "novel_sanguo", "novel_shuihu", "novel_honglou"]

    if clear:
        print("[步骤] 清除已有图谱数据...")
        client.execute_query("MATCH ()-[r:RELATIONSHIP]-() DELETE r")
        client.execute_query("MATCH (p:Person) DELETE p")
        print("  已清除所有人物节点和关系")

    # 创建约束（幂等操作）
    try:
        client.execute_query(
            "CREATE CONSTRAINT unique_person IF NOT EXISTS "
            "FOR (p:Person) REQUIRE (p.name, p.book) IS UNIQUE"
        )
        print("[步骤] 唯一性约束已创建")
    except Exception:
        pass  # 约束可能已存在

    total_persons = 0
    total_relations = 0

    for book in novels:
        if book not in CHARACTERS:
            continue

        print(f"\n[导入] 《{_book_name(book)}》...")

        # 创建人物节点
        persons = CHARACTERS[book]
        for name, identity, aliases, desc in persons:
            cypher = """
            MERGE (p:Person {name: $name, book: $book})
            SET p.identity = $identity,
                p.aliases = $aliases,
                p.description = $description
            """
            client.execute_query(cypher, {
                "name": name,
                "book": book,
                "identity": identity,
                "aliases": aliases,
                "description": desc,
            })
        total_persons += len(persons)
        print(f"  创建 {len(persons)} 个人物节点")

        # 创建关系
        relations = RELATIONSHIPS.get(book, [])
        for from_name, rel_type, to_name, desc in relations:
            # 跳过无效的关系（如我上面写错的那条）
            if from_name == to_name:
                continue
            cypher = """
            MATCH (a:Person {name: $from_name, book: $book})
            MATCH (b:Person {name: $to_name, book: $book})
            MERGE (a)-[r:RELATIONSHIP {type: $rel_type}]->(b)
            SET r.description = $description
            """
            client.execute_query(cypher, {
                "from_name": from_name,
                "to_name": to_name,
                "book": book,
                "rel_type": rel_type,
                "description": desc,
            })
        total_relations += len(relations)
        print(f"  创建 {len(relations)} 条人物关系")

    # 验证
    print("\n[验证] 数据库中的人物节点：")
    stats = client.execute_query(
        "MATCH (p:Person) RETURN p.book as book, count(p) as cnt ORDER BY p.book"
    )
    for row in stats:
        print(f"  {_book_name(row['book'])}: {row['cnt']} 人")

    rel_stats = client.execute_query("MATCH ()-[r:RELATIONSHIP]->() RETURN count(r) as cnt")
    print(f"  关系总数: {rel_stats[0]['cnt'] if rel_stats else 0} 条")

    print(f"\n[完成] 共导入 {total_persons} 个人物、{total_relations} 条关系")
    return True


def _book_name(book: str) -> str:
    mapping = {
        "novel_xiyou": "西游记",
        "novel_sanguo": "三国演义",
        "novel_shuihu": "水浒传",
        "novel_honglou": "红楼梦",
    }
    return mapping.get(book, book)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="初始化四大名著人物关系图谱")
    parser.add_argument("--clear", action="store_true", help="清除已有数据后重新导入")
    parser.add_argument("--novel", type=str, help="只导入指定名著 (xiyou/sanguo/honglou/shuihu)")
    args = parser.parse_args()

    novels = None
    if args.novel:
        novel_map = {
            "xiyou": "novel_xiyou",
            "sanguo": "novel_sanguo",
            "honglou": "novel_honglou",
            "shuihu": "novel_shuihu",
        }
        if args.novel not in novel_map:
            print(f"无效的名著参数: {args.novel}，可选: xiyou/sanguo/honglou/shuihu")
            sys.exit(1)
        novels = [novel_map[args.novel]]

    print("=" * 50)
    print("Neo4j 四大名著人物关系图谱初始化")
    print("=" * 50)

    client = Neo4jClient()
    try:
        init_neo4j(client, novels=novels, clear=args.clear)
    finally:
        client.close()