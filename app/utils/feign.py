import os
import requests

def save_survey(survey_data):
    result = _call_api("POST", "/surveys/", json_data=survey_data)
    if result["success"]:
        result["message"] = "설문 데이터가 성공적으로 저장되었습니다!"
    else:
        if "API 요청 실패" in result["message"]:
            result["message"] = result["message"].replace("API 요청 실패", "설문 데이터 저장 실패")
    return result

def get_recent_surveys():
    result = _call_api("GET", "/surveys/recent")
    if not result["success"]:
        if "API 요청 실패" in result["message"]:
            result["message"] = result["message"].replace("API 요청 실패", "최근 설문 데이터 불러오기 실패")
    return result

def get_survey_by_id(survey_id):
    result = _call_api("GET", f"/surveys/{survey_id}")
    if not result["success"]:
        if "API 요청 실패" in result["message"]:
            result["message"] = result["message"].replace("API 요청 실패", "설문 데이터 불러오기 실패")
    return result

def start_analysis_workflow(survey_id):
    result = _call_api("POST", f"/workflow/analysis/{survey_id}", stream=True)
    return result


def _call_api(method, path, json_data=None, stream=None):
    API_BASE_URL = os.getenv("API_BASE_URL")
    if not API_BASE_URL:
        return {"success": False, "message": "API_BASE_URL 환경 변수가 설정되지 않았습니다."}

    url = f"{API_BASE_URL}{path}"
    try:
        if method == "POST":
            response = requests.post(url, 
                                     json=json_data, 
                                     stream=stream,
                                     headers={"Content-Type": "application/json"})
        elif method == "GET":
            response = requests.get(url)
        else:
            return {"success": False, "message": f"지원하지 않는 HTTP 메서드: {method}"}

        if response.status_code == 200:
            if stream:
                return {"success": True, "data": response}
            else:
                return {"success": True, "data": response.json()}
        else:
            return {"success": False, "message": f"API 요청 실패: {response.status_code} - {response.text}"}
    except requests.exceptions.ConnectionError:
        return {"success": False, "message": "FastAPI 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인해주세요."}
    except Exception as e:
        return {"success": False, "message": f"오류 발생: {e}"}