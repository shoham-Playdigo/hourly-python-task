import requests
import pandas as pd
import math
import json

# --- 1. API Setup ---
url = "https://dashapi.xe.works/playdigo/dsp"
headers = {
    "Authorization": "Bearer 06cff86b858bf78c607bcc0f6ff4419f"
}

# --- 2. Get All DSPs ---
response = requests.get(url, headers=headers)
data = response.json()["data"]

# --- 3. Filter DSPs by Company ---
company_ids_to_keep = [58, 75, 57, 56]  # Inmobi, Adform, FreeWheel, Onetag
filtered_dsps = [dsp for dsp in data if dsp.get("company_id") in company_ids_to_keep]

# --- 4. Fetch Full Details For Each DSP, Ensure sRPM and company_id Are Present ---
all_dsp_details = []
for dsp in filtered_dsps:
    dsp_id = dsp["id"]
    detail_resp = requests.get(f"{url}/{dsp_id}", headers=headers)
    detail_data = detail_resp.json().get("data", {})
    # Always copy sRPM and company_id from summary to details
    detail_data["sRPM"] = dsp.get("sRPM")
    detail_data["company_id"] = dsp.get("company_id")
    all_dsp_details.append(detail_data)
    print(f"Fetched details for DSP ID: {dsp_id} (company_id: {dsp.get('company_id')}, sRPM: {dsp.get('sRPM')})")

# --- 5. Save All DSP Details to Excel ---
pd.DataFrame(all_dsp_details).to_excel("all_dsp_details.xlsx", index=False)
print("Excel file 'all_dsp_details.xlsx' created.")

# --- 6. QPS Update Logic for Each DSP ---

def build_company(obj):
    default = {"id": 10, "name": "Company Name", "api_key": "random-string"}
    if "Company" in obj:
        comp = obj["Company"]
        return {
            "id": comp.get("id", default["id"]),
            "name": comp.get("name", default["name"]),
            "api_key": comp.get("api_key", default["api_key"])
        }
    return default

def build_size(obj):
    return obj.get("Size", [{"code": "string"}])

def build_operating_system(obj):
    return obj.get("OperatingSystem", [{"key": "string", "name": "string"}])

def build_ssp(obj):
    return obj.get("Ssp", {
        "allowedSsp": [{"ssp_id": 9007199254740991}],
        "blockedSsp": [{"ssp_id": 9007199254740991, "name": "string"}]
    })

def build_platforms(obj):
    return obj.get("Platforms", {
        "allowedPlatforms": [{"type": "app", "source": "string"}],
        "blockedPlatforms": [{"type": "app", "source": "string"}]
    })

def build_country(obj):
    return obj.get("Country", [{"country_code": "str"}])

def build_platform_lists(obj):
    return obj.get("PlatformLists", [{
        "id": 9007199254740991,
        "name": "string",
        "applyAll": 0,
        "type": "string",
        "status": 0
    }])

def build_old_data(dsp):
    return {
        "id": dsp.get("id"),
        "api_endpoint": dsp.get("api_endpoint", ""),
        "Company": build_company(dsp),
        "Size": build_size(dsp),
        "OperatingSystem": build_operating_system(dsp),
        "Ssp": build_ssp(dsp),
        "Platforms": build_platforms(dsp),
        "Country": build_country(dsp),
        "PlatformLists": build_platform_lists(dsp)
    }

def build_updated_data(dsp, new_qps_limit):
    return {
        "id": dsp.get("id"),
        "name": dsp.get("name", "string"),
        "integrationType": dsp.get("integration_type", "rtb"),
        "endpoint": dsp.get("endpoint", "string"),
        "inventory_partner_domain_enabled": dsp.get("inventory_partner_domain_enabled", 0),
        "cpm": dsp.get("cpm", 0),
        "cpm_seller": dsp.get("cpm_seller", 0),
        "tag": dsp.get("tag", "string"),
        "min_floor": dsp.get("min_floor", 0),
        "max_floor": dsp.get("max_floor", 0),
        "spend_limit": dsp.get("spend_limit", 0),
        "min_tmax": dsp.get("min_tmax", 0),
        "set_tmax": dsp.get("set_tmax", 0),
        "qps_limit": new_qps_limit,
        "isBanner": dsp.get("isBanner", 0),
        "isNative": dsp.get("isNative", 0),
        "isVideo": dsp.get("isVideo", 0),
        "isAudio": dsp.get("isAudio", 0),
        "isNurl": dsp.get("isNurl", 1),
        "is_gzip": dsp.get("is_gzip", 0),
        "schain": dsp.get("schain", 0),
        "schain_direct_list_id": dsp.get("schain_direct_list_id", 0),
        "schain_indirect_list_id": dsp.get("schain_indirect_list_id", 0),
        "isSensitive": dsp.get("isSensitive", 0),
        "device_config": dsp.get("device_config", "{\"m\": true, \"d\": true, \"c\": true}"),
        "ad_config": dsp.get("ad_config", "{\"w\":true,\"ia\":true}"),
        "prebid_config": dsp.get("prebid_config", "string"),
        "adapter_config": dsp.get("adapter_config", "string"),
        "smartad_config": dsp.get("smartad_config", "string"),
        "marga": dsp.get("marga", 0),
        "demand_fee": dsp.get("demand_fee", 0),
        "api_endpoint": dsp.get("api_endpoint", "string"),
        "ifa_only": dsp.get("ifa_only", 0),
        "fixedCPM": dsp.get("fixedCPM", 0),
        "filter_max_schain_length": dsp.get("filter_max_schain_length", 0),
        "scan_cfg": dsp.get("scan_cfg", "string"),
        "omsdk": dsp.get("omsdk", 0),
        "intent_iq": dsp.get("intent_iq", "string"),
        "impression_limit": dsp.get("impression_limit", 0),
        "vpaid_disabled": dsp.get("vpaid_disabled", 0),
        "gdpr_consented": dsp.get("gdpr_consented", 0),
        "pchain": dsp.get("pchain", 0),
        "is_throttled": dsp.get("is_throttled", 1),
        "srpm_goal": dsp.get("srpm_goal", 0.1),
        "auction_type": dsp.get("auction_type", "string"),
        "Size": build_size(dsp),
        "OperatingSystem": build_operating_system(dsp),
        "Ssp": build_ssp(dsp),
        "Platforms": build_platforms(dsp),
        "Country": build_country(dsp),
        "PlatformLists": build_platform_lists(dsp)
    }

# -- Run QPS logic and send PUTs only as needed --
update_info = []
for dsp in all_dsp_details:
    dsp_id = dsp.get("id")
    dsp_name = dsp.get("name")
    sRPM = dsp.get("sRPM", 0)
    qps_limit = dsp.get("qps_limit", 0)
    real_qps = dsp.get("real_qps", 0)
    action = "none"
    new_qps_limit = qps_limit

    # Print debug info for each DSP
    print(f"Checking DSP ID {dsp_id} ({dsp_name}): sRPM={sRPM}, QPS_limit={qps_limit}, real_qps={real_qps}")

    # --- QPS INCREASE LOGIC ---
    if (
        sRPM is not None and
        sRPM >= 1 and
        500 < qps_limit < 30000 and
        real_qps >= 0.7 * qps_limit
    ):
        action = "increase"
        new_qps_limit = math.ceil(min(qps_limit * 1.15, 30000))
        print(f"  - Increase logic applied.")
    # --- QPS DECREASE LOGIC ---
    elif (
        sRPM is not None and
        sRPM < 0.4 and
        qps_limit > 500
    ):
        action = "decrease"
        new_qps_limit = math.ceil(max(qps_limit * 0.85, 500))
        print(f"  - Decrease logic applied.")
    else:
        print(f"  - No QPS change.")

    status = "Unchanged/skipped"
    if new_qps_limit != qps_limit:
        payload = {
            "oldData": build_old_data(dsp),
            "updatedData": build_updated_data(dsp, new_qps_limit)
        }
        put_url = f"{url}/{dsp_id}"
        put_resp = requests.put(put_url, headers={**headers, "Content-Type": "application/json"}, json=payload)
        status = "Success" if put_resp.status_code == 200 else f"Failed (HTTP {put_resp.status_code})"
        print(f"  - Updated DSP: QPS limit from {qps_limit} to {new_qps_limit}. Status: {status}")

    update_info.append({
        "dsp_id": dsp_id,
        "dsp_name": dsp_name,
        "old_qps_limit": qps_limit,
        "new_qps_limit": new_qps_limit,
        "sRPM": sRPM,
        "real_qps": real_qps,
        "logic_applied": action,
        "status": status
    })

# --- 7. Save Update Results to Excel ---
pd.DataFrame(update_info).to_excel("qps_update_result.xlsx", index=False)
print("Excel file 'qps_update_result.xlsx' created with QPS update information.")
