"""
database/seed_articles.py - NAP DU LIEU MAU (DUMMY DATA)

Theo yeu cau cua De tai 06:
    "Database goc: Toi thieu 100 Bai viet hoan chinh co tieu de, noi dung va hinh anh"

Script nay se:
    1. Tao 3 tai khoan demo (sv1/sv2/sv3) trong collection `users`
    2. Tao 100 bai viet day du: tieu de, tom tat, noi dung, hinh anh, chuyen muc, the
    3. Sinh 100 anh JPEG (1200x675) bang Pillow vao static/uploads/

Chay:  python database/seed_articles.py  [--reset]
"""

import argparse
import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from pymongo import MongoClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import config  # noqa: E402
from models import article as article_model  # noqa: E402
from models import user as user_model  # noqa: E402

# ------------------------------------------------------------------
# Dinh mau (deterministic) - chay lai van ra cung du lieu
# ------------------------------------------------------------------
random.seed(2026)

TOTAL_ARTICLES = 100
IMAGE_SIZE = (1200, 675)

DEMO_USERS = [
    ("sv1_admin", "sv1@uit.edu.vn", "SV1 - Data Architect", "admin"),
    ("sv2_editor", "sv2@uit.edu.vn", "SV2 - Cache Specialist", "editor"),
    ("sv3_editor", "sv3@uit.edu.vn", "SV3 - Fullstack Integrator", "editor"),
]
DEMO_PASSWORD = "123456"

# Mau sac theo chuyen muc (dung cho hinh anh)
PALETTE = {
    "Cong nghe": ((13, 110, 253), (0, 82, 204)),
    "Kinh te": ((25, 135, 84), (10, 94, 60)),
    "The thao": ((255, 102, 0), (190, 70, 0)),
    "Khoa hoc": ((108, 92, 231), (70, 52, 190)),
    "Xa hoi": ((214, 51, 132), (160, 30, 95)),
    "Doi song": ((23, 162, 184), (10, 120, 140)),
}

# Tieu de theo chuyen muc - sinh ra >= 100 tieu de duy nhat
TITLES = {
    "Cong nghe": [
        "Cong nghe AI bien doi cach nganh xay dung phan mem",
        "Redis 8.10 ra mat: nhung nang luc dang chu y",
        "MongoDB Atlas tang cuong ha tang du lieu toan cau",
        "Xu huong microservices tai Viet Nam nam 2026",
        "Ky thuat cache phia may chu giup phan mem nhanh hon bao lao",
        "Docker va container hoa du lieu: nen tang hay xu huong that",
        "Python 3.13 ra mat: nhung thay doi dang chu y",
        "WebAssembly co the thay doi cach chay ung dung web",
        "Bao mat du lieu trong chu ky bao ho data breach",
        "Flutter bo khung xu huong ung dung di dong mot lan",
        "Thi tuong tai: ha tang tinh toan cho mo hinh AI",
        "REST API hay GraphQL: lua chon nao phu hop hon",
        "GitHub Copilot va vai tro cua AI trong lap trinh",
        "Hieu nhat ve index trong MongoDB de truy van nhanh hon",
        "MERN stack: su dung cong nghe nao trong du an thuc te",
        "Dich vu cloud so sanh giua AWS, Azure va Google Cloud",
        "Phat trien API an toan theo chuan RESTful",
        "Xu huong serverless va tac dong den ha tang du lieu",
        "Chuan hoa du lieu JSON: phia truoc moi khau xu ly du lieu lon",
        "Nen tang quan ly dich vu microservice cho doanh nghiep",
        "Bai hoc tu viec trien khai he thong phan tan tai TP.HCM",
        "Kien truc lam voi (Event-Driven) khac gi voi kiến trúc thuoc tinh",
        "Redis Sentinel: giu cho Redis luon hoat dong",
        "Xu huong quan sat du lieu voi OpenTelemetry",
        "Bai toan ton tai du lieu trong MongoDB replica set",
    ],
    "Kinh te": [
        "Lam phat kinh te Q3: cac chi so dang chu y",
        "Nganh ngan hang so duy tri cong nghe blockchain",
        "Thi truong bat dong san phan hoa sau chu kich lam phat",
        "Xu huong xanh hoa va co hoi cho doanh nghiep nho",
        "Chi phi logistics tang, doanh nghiep xuat khau xu ly ra sao",
        "Tien te so hoa va tac dong den ngan hang Viet Nam",
        "Doanh nghia chung khoan ky vong mua cua nam 2026",
        "Kinh te so hoa: co hoi hay thach thuc cho doanh nghia",
        "Doanh nhu trong ban le hang hoa cua nganh cong nghhe",
        "Nganh du lich phuc hoi manh me sau giai doan dich COVID",
        "Phong cach mua sam trong chu ky kinh te hien tai",
        "Rui ro lam phat lam phat lam phat o cap dia phuong",
        "Nganh ban le dung chung nhan dien tu",
        "Chi phi von: doanh nghia nao dang dauu tu",
        "Hop tac kinh doanh chia se loi nhuan song song",
        "Xu huong ban kinh doanh theo mo hinh chia se tai nguyen",
        "Vai tro cua du lieu lon trong quyet dinh kinh doanh",
        "Chi phi logistics va tac dong den gia hang thuoc pham",
        "Kinh doanh xanh: co hoi tu chuyen doi nang luong",
        "Nganh bao hiem so doi hoa quy trinh ban hang",
    ],
    "The thao": [
        "Giai Vo Le Dich bat ngo doi chuyen luu",
        "Doi tuyen Olympic 2026 chinh thuc len danh sach",
        "Bong da Viet Nam chuan bi moi sau chu ky vang dong",
        "Thanh thu bo sung bao ve luoi vien tan bien",
        "Bang xep hang the gioi ban cap nhat nhanh chong",
        "The thao thu cong: nen tang dac biet cua nguyen nen tao",
        "Chuyen gia bao len xu huong chay bo tai chuong trinh chay",
        "CLB bien dau co ban nguon luc tai day",
        "Ky nang tan bien cua ngon ai trong the thao thu cong",
        "The thao dien tu: xu huong lan rong tai Viet Nam",
        "Hoi muon truc tiep dang thay doi cach the thao duoc gia",
        "Sau chuc nhan giai Vong 1: ket qua ngoai mong",
        "The thao trong truong hoc: huong denh thuc mo rong",
        "Chuyen gia binhluan cua tran chung ket si Viet Nam",
        "Ky luc moi cua nen the thao trong nu",
        "Nghi thuc the thao bo phan: bai hoc tu the gioi",
    ],
    "Khoa hoc": [
        "May tro khang tim ra loai phan tu moi trong bang cach",
        "Telescope khong gian chup duoc anh chup bao kiem moi",
        "Nghien cuu moi ve te bao va ung dung trong dieu tri",
        "Bien doi khi hau va tac dong len an ninh luu tru",
        "Cong nghe nano trong chan doan y te som",
        "Tinh huong bien mat truc tiep trong huong nghien",
        "Vai tro cua AI trong nghien cuu khoa hoc",
        "San xuat thuc an tu thuc vat: xu huong moi",
        "Bua hoc cap nhan so lieu ve bien doi khi hau toan cau",
        "Nha khoa hoc Viet Nam cong bo phat hien moi",
        "Nghien cuu moi ve bien do du lieu dai duong bien",
        "Cong nghe luu tru moi huong toi bang gia soi nhan thuc",
        "Vai tro cua may dien toan luong trong nghien cuu bien khi hau",
        "Nghien cuu moi ve vat lieu de chan phong dien tu",
    ],
    "Xa hoi": [
        "Ha noi phat hanh ke hoach giao thong moi nam 2026",
        "Nghien cuu moi ve muc song chung cua nguoi lao dong",
        "Phong trong tai cong cong vien ky van hien tuong tren",
        "Ky thuat so doi doi voi nghiep vu hanh chinh cong",
        "Nghien cuu ve thay doi moi truong duong song thien",
        "Phan bienh ve du lich canh trong nhom bon chon",
        "Doi song ngoi thanh: sau sang huu nghiep",
        "Kien nghi ve cap nhan cam bao gia dinh",
        "Anh huong cua truyen thong so den hanh vi xa hoi",
        "Nghien cuu moi ve muc hieu biet cua nguoi tieu dung",
        "Chuong trinh tu nguyen gia dinh co hoa thuong",
        "Mo hinh kinh doanh chia se tai cong ty cong",
        "Nghien cuu ve muc thu nhap cua ho gia dinh tai TP.HCM",
        "Vai tro cua cong cong truc tuyen trong thoi gian gian cach",
    ],
    "Doi song": [
        "Ngonh thuc an lienh giup tang nang luong buoi sang",
        "Huong nghi thoi gian lai: xu huong cua nguoi tre",
        "Lam sao de chon nem giu ngon hieu kinh nghiem",
        "Du lich mua sam ket hop nghi duong tai mien Bac",
        "Bua an dinh duong va cach tinh luong cho nguoi ngoi",
        "Xu huong lam dep va bao hiem suc khoe trong 2026",
        "Cong nghe thong minh thay doi cach chung ta chon thuc an",
        "Boi duong thoi khoang trong nhom viec cong so",
        "Son do hien trong thoi gian lam viec",
        "Cach chon qua tet cho nguoi lam viec",
        "Thoii qu doc sach giup tang tap trung tot hon",
    ],
}

SUMMARIES = [
    "Bai viet phan tich nhin va thay doi dang gay chuyen nganh trong thoi gian gan day.",
    "Nhieu thay doi dang duoc ghi nhan va cac chuyen gia nhan dinh danh giá se ra sao.",
    "Cong ty va co quan chuc nang lien quan da ban hanh huong dan moi truoc doi.",
    "So lieu moi nhat cho thay muc do phat trien dang duoc nang cao nhanh chong.",
    "Bai viet tong hop cac thong tin dang duoc quan tam trong cộng dong.",
    "Ket qua kiem chung cho thay huong nghien dang dua ra nhung buoc tien ro ret.",
]

PARAGRAPHS = [
    "Trong boi canh ky thuat va kinh te dang bien doi nhanh, sucEp vao moi truong can duoc nhan dinh dung dac biet. "
    "Cac chuyen gia nhan dinh rang nhung thay doi nay khong chi den mot linh vuc ma con lan rong ra nhieu nganh khac nhau.",
    "Theo so lieu moi cong bo, chi so tang truong lien tiep trong nhieu thang qua. "
    "Dieu nay cho thay nhu cau va nguon luc dang duoc day len trong thoi gian dai, ke ca voi doanh nghia vua va nho.",
    "Ban chi dao bo phan tap theo danh gia, viet trang, cac yeu too ky thuat va nhan su se la nhung yeu too then chot trong giai doan moi. "
    "Song song do, y eu cau bao dam chat luong va an toan duoc dat len hang dau.",
    "Khach hang ngay cang co ky vong cao hon, yeu cau dich vu nhanh, on dinh va de su dung. "
    "Vi vay, muc tieu dang nam giua chong nghiep, tang nang suat va phat trien bai toan kinh doanh ben vung.",
    "Dinh huong trong ngan han ke tiep se tap trung vao nang cao nang luc chuyen doi so, "
    "mo rong pham vi hop tac va nang cao nang luc canh tranh cho cac doanh nghia trong nganh.",
    "Doi voi nguoi dan, thay doi dich trong thoi gian nganh nua cung khong kho nho. "
    "Nhieu gia phap da duoc de xuat va mot so mo hinh thu nghiem da nhan duoc su quan tam.",
    "Ket qua cua dot kiem tra cho thay phan lon nhan dinh dung phuong an dang duoc trien khai co hieu qua. "
    "Tuy nhien, can bo sung them cac bai toan ve an toinh thong tin va bao dam chat luong du lieu.",
    "Nhieu chuyen gia cho rang buoc nam toi nguon luc va con duong giai phap se phu thuoc vao muc do chuan bi cua chinh sach.",
    "Trong ngan han, cac don vi dang nang cao nang luc doi moi, chu dong dua san cong nghe vao hoat dong. "
    "Cach tiep can nay duoc ky vong tao ra nhung dot phat trien moi ve chat luong dich vu.",
    "Truong hop nghien cuu duoc dau ra moi, phuong phap dieu chinh se duoc dieu chinh phu hop voi dac thuyet va thuc te.",
    "Buoc tiep theo la trien khai rong rai va danh gia hieu qua o nhieu dia phuong truoc khi toan dien. "
    "Ket qua se duoc cong bo kep theo bao cao danh gia dinh ky.",
    "Song song, cac dau moi nghi thuc chuyen mon duoc to chuc va phat trien nang cao chat luong hoi dap.",
]


def _font(size, bold=False):
    """Load font Windows (fallback ve font mac dinh cua Pillow)."""
    candidates = [
        Path("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf"),
        Path("C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf"),
        Path("C:/Windows/Fonts/calibrib.ttf" if bold else "C:/Windows/Fonts/calibri.ttf"),
    ]
    for path in candidates:
        if path.exists():
            try:
                return ImageFont.truetype(str(path), size)
            except OSError:
                continue
    return ImageFont.load_default()


def generate_image(index, title, category, out_dir: Path):
    """
    Sinh 1 anh JPEG 1200x675 cho bai viet (khong can tai tu Internet,
    do la demo offline hoan toan).
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    filename = f"news_{index:03d}.jpg"
    path = out_dir / filename

    c1, c2 = PALETTE.get(category, ((13, 110, 253), (0, 82, 204)))
    width, height = IMAGE_SIZE

    # Nen gradient
    image = Image.new("RGB", (width, height), c1)
    draw = ImageDraw.Draw(image)
    for y in range(height):
        ratio = y / height
        color = (
            int(c1[0] + (c2[0] - c1[0]) * ratio),
            int(c1[1] + (c2[1] - c1[1]) * ratio),
            int(c1[2] + (c2[2] - c1[2]) * ratio),
        )
        draw.line([(0, y), (width, y)], fill=color)

    # Hinh trang trí
    draw.ellipse([width - 320, -160, width + 160, 320], outline=(255, 255, 255), width=4)
    draw.ellipse([-180, height - 240, 220, height + 160], outline=(255, 255, 255), width=4)
    draw.rectangle([60, 60, width - 60, height - 60], outline=(255, 255, 255), width=3)

    # Chu
    font_cat = _font(44, bold=True)
    font_no = _font(150, bold=True)
    font_title = _font(38, bold=True)

    draw.text((100, 110), category.upper(), font=font_cat, fill=(255, 255, 255))
    draw.text((100, height - 260), f"#{index:03d}", font=font_no, fill=(255, 255, 255))

    # Cat tieu de la 2 dong
    words = title.split()
    line, lines = "", []
    for word in words:
        if len(line + " " + word) > 38:
            lines.append(line)
            line = word
        else:
            line = (line + " " + word).strip()
    if line:
        lines.append(line)
    y = height - 150
    for text_line in lines[:2]:
        draw.text((100, y), text_line, font=font_title, fill=(255, 255, 255))
        y += 52

    image.save(path, "JPEG", quality=82, optimize=True)
    return f"/static/uploads/{filename}"


def seed_users(db):
    """Tao 3 tai khoan demo (mat khau chung: 123456)."""
    created = []
    for username, email, full_name, role in DEMO_USERS:
        if user_model.find_by_email(db, email):
            print(f"  [skip] Tai khoan {username} da ton tai")
            continue
        user_model.create_user(
            db,
            username=username,
            email=email,
            password=DEMO_PASSWORD,
            full_name=full_name,
            role=role,
        )
        created.append(username)
    return created


def seed_articles(db, upload_dir: Path, reset=False):
    """Tao 100 bai viet hoan chinh + 100 anh."""
    if reset:
        db["articles"].delete_many({})
        print("  Da xoa toan bo bai viet cu")

    existing = db["articles"].count_documents({})
    if existing >= TOTAL_ARTICLES:
        print(f"  [skip] Da co {existing} bai viet trong DB")
        return existing

    index = existing
    created = 0
    for category, titles in TITLES.items():
        for title in titles:
            index += 1
            if index > TOTAL_ARTICLES:
                break
            image_path = generate_image(index, title, category, upload_dir)

            paragraphs = random.sample(PARAGRAPHS, k=min(5, len(PARAGRAPHS)))
            content = "\n\n".join(paragraphs)
            summary = random.choice(SUMMARIES)
            tags = [w.lower() for w in title.split()[:4] if len(w) > 4]

            article_model.create_article(
                db,
                {
                    "title": title,
                    "summary": summary,
                    "content": content,
                    "image": image_path,
                    "category": category,
                    "tags": tags,
                    "status": "published",
                },
                author_id=None,
                author_name="To So Bien Tap",
            )
            created += 1
    return created


def main():
    parser = argparse.ArgumentParser(description="Nap du lieu mau cho De tai 06")
    parser.add_argument("--reset", action="store_true", help="Xoa du lieu cu truoc khi nap")
    args = parser.parse_args()

    print("=" * 64)
    print("  SEED DU LIEU MAU - De tai 06 (Cache-Aside + Session Management)")
    print("=" * 64)

    client = MongoClient(config.MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client[config.MONGO_DB_NAME]
    client.admin.command("ping")
    print(f"MongoDB   : {config.MONGO_URI} / {config.MONGO_DB_NAME}")

    user_model.ensure_indexes(db)
    article_model.ensure_indexes(db)

    print("\n[1/3] Tai khoan demo:")
    for username in seed_users(db):
        print(f"  + {username} / {DEMO_PASSWORD}")

    print(f"\n[2/3] Bai viet + hinh anh (muc tieu {TOTAL_ARTICLES}):")
    created = seed_articles(db, config.UPLOAD_FOLDER, reset=args.reset)
    print(f"  + Da tao {created} bai viet va {created} anh vao {config.UPLOAD_FOLDER}")

    print("\n[3/3] Kiem tra:")
    print(f"  Tong so bai viet : {db['articles'].count_documents({})}")
    print(f"  Tong so nguoi dung: {db['users'].count_documents({})}")
    print(f"  Chuyen muc       : {article_model.distinct_categories(db)}")
    print("\nHoan tat! Chay 'python app.py' de kiem tra tren trinh duyet.")
    print("=" * 64)


if __name__ == "__main__":
    main()
