import os
import requests

# 저장할 폴더
save_dir = "set_cards"
os.makedirs(save_dir, exist_ok=True)

# 4자리 3진수 조합 생성 (0000 ~ 2222, 총 81개)
for color in range(3):
    for shape in range(3):
        for shading in range(3):
            for number in range(3):
                filename = f"{color}{shape}{shading}{number}.png"
                url = f"https://uiqoo.kr/boardgames/setboardgame/{filename}"
                response = requests.get(url)

                if response.status_code == 200:
                    with open(os.path.join(save_dir, filename), "wb") as f:
                        f.write(response.content)
                    print(f"✅ Saved: {filename}")
                else:
                    print(f"❌ Failed to download: {filename}")
