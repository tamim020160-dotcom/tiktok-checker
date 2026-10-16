import streamlit as st
import requests
import json

st.set_page_config(page_title="فاحص حسابات تيك توك", page_icon="📱", layout="centered")

st.title("📱 فاحص ومعلومات حسابات تيك توك")
st.write("أدخل اسم المستخدم (اليوزر) لجلب إحصائيات الحساب مباشرة عبر موقعك المجاني.")

username = st.text_input("أدخل يوزر تيك توك (بدون @):", placeholder="مثلاً: khaby.lame")

if st.button("فحص الحساب"):
    if not username:
        st.warning("الرجاء إدخال اسم المستخدم أولاً.")
    else:
        with st.spinner(f"جاري سحب بيانات الحساب: {username}..."):
            url = f"https://m.tiktok.com/@{username}"
            headers = {
                "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
                "Accept-Language": "en-US,en;q=0.9",
                "Referer": "https://www.tiktok.com/"
            }
            
            try:
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code != 200:
                    st.error(f"خطأ في الوصول للحساب. الرمز: {response.status_code}")
                else:
                    html = response.text
                    marker = '<script id="SIGI_STATE" type="application/json">'
                    start_idx = html.find(marker)
                    if start_idx == -1:
                        marker = '<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__" type="application/json">'
                        start_idx = html.find(marker)
                        
                    if start_idx == -1:
                        st.error("لم يتم العثور على بيانات المستخدم (تيك توك يحمي الصفحة حالياً ضد السحب المباشر أو الحساب غير موجود).")
                    else:
                        start_idx += len(marker)
                        end_idx = html.find("</script>", start_idx)
                        if end_idx == -1:
                            st.error("فشل استخراج هيكل البيانات.")
                        else:
                            json_data = html[start_idx:end_idx]
                            data = json.loads(json_data)
                            
                            user_module = data.get("UserModule", {}).get("users", {}).get(username, {})
                            stats_module = data.get("UserModule", {}).get("stats", {}).get(username, {})
                            
                            if not user_module:
                                st.warning("الحساب موجود ولكن تعذر جلب تفاصيله بسبب تحديثات تيك توك.")
                            else:
                                st.success("تم جلب البيانات بنجاح! 🎉")
                                st.json({
                                    "معرف المستخدم (UID)": user_module.get("id"),
                                    "اسم المستخدم": user_module.get("uniqueId"),
                                    "الاسم المستعار": user_module.get("nickname"),
                                    "عدد المتابعين": stats_module.get("followerCount"),
                                    "عدد المتابَعين": stats_module.get("followingCount"),
                                    "إجمالي الإعجابات": stats_module.get("heartCount"),
                                    "عدد الفيديوهات": stats_module.get("videoCount"),
                                    "حساب موثق": user_module.get("verified"),
                                    "حساب خاص": user_module.get("privateAccount")
                                })
            except Exception as e:
                st.error(f"حدث خطأ أثناء الاتصال: {str(e)}")
