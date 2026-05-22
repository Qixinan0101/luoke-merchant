# 杩滆鍟嗕汉 路 瀹炴椂鍟嗗搧

娲涘厠鐜嬪浗涓栫晫 鈥?杩滆鍟嗕汉姣忔棩鍟嗗搧瀹炴椂鏌ヨ App

## 鍔熻兘

- 馃摝 **瀹炴椂鍟嗗搧鏁版嵁** 鈥?閫氳繃 GitHub Actions 姣?5鍒嗛挓鑷姩浠?onebiji.com 鎶撳彇
- 鈴?**鍒锋柊鍊掕鏃?* 鈥?瀹炴椂鏄剧ず璺濅笅涓€杞粨鏉熺殑鍊掕鏃?- 馃攧 **4杞垏鎹?* 鈥?鐐瑰嚮鏍囩鏌ョ湅姣忚疆鍟嗗搧锛?8:00 / 12:00 / 16:00 / 20:00锛?- 馃摫 **鎵嬫満閫傞厤** 鈥?涓撲负鎵嬫満灞忓箷璁捐锛屽崟鎵嬪彲鎿嶄綔
- 馃攣 **鑷姩鍒锋柊** 鈥?姣?0绉掕嚜鍔ㄦ媺鍙栨渶鏂版暟鎹?- 馃柤 **鍟嗗搧鍥剧墖** 鈥?鐩存帴鏄剧ず娓告垙鍐呴亾鍏峰浘鏍?- 馃晲 **鏅鸿兘鐘舵€?* 鈥?鑷鍒ゆ柇鍖椾含鏃堕棿锛屼笉渚濊禆鏁版嵁婧愮殑 status 瀛楁

## 鏁版嵁绠￠亾

```
onebiji.com锛堟簮澶达級
    鈫?GitHub Actions 姣?5鍒嗛挓鎶撳彇
鎴戜滑鑷繁鐨?data/merchant.json
    鈫?鎵樼鍦?GitHub
App 鐩存帴璇诲彇锛堝疄鏃躲€佸彲鎺э級
```

- 鏁版嵁鎶撳彇鍣細`fetch_merchant.py` 鈥?Python 鑴氭湰锛屼粠 onebiji.com 瑙ｆ瀽鍟嗗搧
- 瀹氭椂浠诲姟锛歚.github/workflows/fetch-merchant.yml` 鈥?姣忓ぉ 08:00-24:00 姣?5鍒嗛挓杩愯
- 澶囩敤婧愶細`rocokingdomworld.org/data/merchant.json`锛堝綋鑷湁婧愪笉鍙敤鏃惰嚜鍔ㄥ垏鎹級

## 浣跨敤鍓嶅繀椤婚厤缃?
### 1. 鎺ㄩ€佷唬鐮佸埌 GitHub

```bash
cd E:\ai\luoke-merchant
git init
git add .
git commit -m "杩滆鍟嗕汉App v2.0"
git remote add origin https://github.com/浣犵殑鐢ㄦ埛鍚?luoke-merchant.git
git push -u origin main
```

### 2. 璁剧疆 GitHub Username锛堝湪 App 閲岋級

App 瀹夎鍒版墜鏈哄悗锛屽湪娴忚鍣ㄦ墦寮€涓€娆★紝鎸?F12 鈫?Console 杈撳叆锛?
```js
localStorage.setItem('gh_user', '浣犵殑GitHub鐢ㄦ埛鍚?)
```

鐒跺悗鍒锋柊椤甸潰锛孉pp 灏变細浼樺厛璇诲彇浣犺嚜宸辩淮鎶ょ殑瀹炴椂鏁版嵁銆?
> 涓嶈缃篃娌″叧绯伙紝App 浼氳嚜鍔ㄩ檷绾т娇鐢?rocokingdomworld.org 鐨勫鐢ㄦ暟鎹簮銆?
## 鎵撳寘 APK

### 鏂规硶涓€锛欰ndroid Studio

1. 鐢?Android Studio 鎵撳紑 `android/` 鐩綍
2. Ctrl+F9 鏋勫缓
3. APK 鍦?`android/app/build/outputs/apk/debug/app-debug.apk`

### 鏂规硶浜岋細GitHub Actions 鑷姩鏋勫缓

鎺ㄩ€佷唬鐮佸悗锛屽埌 GitHub 浠撳簱 鈫?Actions 鈫?鏋勫缓杩滆鍟嗕汉 APK 鈫?涓嬭浇 Artifacts

## 椤圭洰缁撴瀯

```
luoke-merchant/
鈹溾攢鈹€ www/
鈹?  鈹斺攢鈹€ index.html           鈫?鏍稿績搴旂敤锛堝崟鏂囦欢锛?鈹溾攢鈹€ data/
鈹?  鈹斺攢鈹€ merchant.json        鈫?GitHub Actions 鑷姩鏇存柊
鈹溾攢鈹€ fetch_merchant.py        鈫?鏁版嵁鎶撳彇鑴氭湰
鈹溾攢鈹€ requirements.txt
鈹溾攢鈹€ android/                 鈫?Capacitor 瀹夊崜椤圭洰
鈹溾攢鈹€ .github/workflows/
鈹?  鈹溾攢鈹€ fetch-merchant.yml   鈫?瀹氭椂鎶撳彇鏁版嵁
鈹?  鈹斺攢鈹€ build-apk.yml        鈫?鍦ㄧ嚎鏋勫缓 APK
鈹溾攢鈹€ build-apk.bat
鈹斺攢鈹€ package.json
```
