import requests, math, json
import time
from tqdm import tqdm

URL = "https://api-maps.viettel.vn/gateway/placeapi/v2-old/place-api/VTMapService/geoprocessing?f=getaddr&"
# pt=16.09385240990386,%20108.12379951945667&k=4474ace29cd4d4fa14847303d2a6d6f0  

# radius Bán kính 10km
def generate_points_around_center(center_lat, center_lon, radius, num_points):
    points = []
    
    for i in range(num_points):
        angle = 2 * math.pi * i / num_points
        dx = radius * math.cos(angle)
        dy = radius * math.sin(angle)
        
        new_lat = center_lat + (180 / math.pi) * (dy / 6371000)
        new_lon = center_lon + (180 / math.pi) * (dx / (6371000 * math.cos(center_lat * math.pi / 180)))
        
        points.append((new_lat, new_lon))
    
    return points

def main(center_point, radius,num_points, json_file_path):
    points = generate_points_around_center(center_point["lat"], center_point["lon"], radius, num_points)
    data = []
    address = []
    num_success_request = 0
    with tqdm(total=len(points), desc="Fetching data: ", bar_format="{l_bar}{bar}        [ time left: {remaining} ]") as pbar:
        for index,point in enumerate(points): 
            if not(index % LIMIT_REQUEST):
                time.sleep(1)
            else:
                #try:
                api_url = f"{URL}pt={point[0]},%20{point[1]}&k=4474ace29cd4d4fa14847303d2a6d6f0"
                response = requests.get(api_url)
                new_address = json.loads(response.text)["data"]
                print(new_address)
                if new_address not in address:
                    address.append(new_address)
                    data_item = {
                        "lat": str(point[0]),
                        "lon": str(point[1]),
                        "address": new_address
                    }
                    data.append(data_item)
                num_success_request = num_success_request + 1
                #except:
                #    pass
            pbar.update(1)
    with open(json_file_path, 'w', encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f"Tổng số điểm: {num_points}, Số request thành công: {num_success_request}/{num_points}, Số điểm dữ liệu thu được: {len(data)}")
       
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- 
# -------------------------------------------------------------------------MAIN------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Note:
# https://maps.viettel.vn/docs/web-js/examples/search-around // vao web để lấy thông tin phạm vi, tọa độ muôn search
# param1 : center_point với định dạng lat, lon như điểm p bên dưới
# param2 : phạm vi bao nhiêu m 
# param3 : Số điểm cần lấy trong phạm vi

center_point = {
    "lat": 16.092933,
    "lon": 108.231273
}
radius = 1500  #10kmm
num_points = 30 # lấy 1000 điểm trong phạm vi này 
json_file_path = "16_092933__108_231273__1500.json" # Đường dẫn file lưu dữ liệu
LIMIT_REQUEST = 100  # Giới hạn số lượng request gửi lên 1 lần

# Gọi hàm để crawl
main(center_point, radius, num_points, json_file_path)