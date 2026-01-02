<!DOCTYPE html>
<html lang="ar" dir="ltr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Verify Identity | DZ-CONNECT</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap" rel="stylesheet">
    <style>
        /* خلفية الصفحة (صورة الفأرة) */
        body { 
            margin: 0; padding: 0;
            background: url('https://z-cdn-media.chatglm.cn/files/df4cae94-bae5-4bf1-8d51-54a2fb4429b7.jpg?auth_key=1867320284-a137d941c33b45ccabec0925b6873bf1-0-677147ce5499656f976e32cfdda66079') no-repeat center center fixed;
            background-size: cover;
            color: white; 
            font-family: 'Cairo', sans-serif;
            min-height: 100vh;
        }

        /* طبقة التعتيم */
        body::before {
            content: "";
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0, 10, 20, 0.5);
            z-index: -1;
        }

        /* البطاقة الزجاجية */
        .glass-card {
            background: rgba(0, 5, 10, 0.7);
            border: 1px solid rgba(0, 242, 255, 0.3);
            backdrop-filter: blur(15px);
            box-shadow: 0 0 40px rgba(0, 242, 255, 0.1);
            transition: 0.3s;
        }

        /* حقل الإدخال */
        .pin-input {
            background: rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.1);
            color: white;
            letter-spacing: 0.5em; /* مسافات بين الأرقام */
            text-shadow: 0 0 10px rgba(0, 242, 255, 0.5);
            transition: 0.3s;
        }
        .pin-input:focus {
            background: rgba(0, 0, 0, 0.5);
            border-color: #00f2ff;
            box-shadow: 0 0 20px rgba(0, 242, 255, 0.3);
            outline: none;
        }

        /* زر التحقق */
        .btn-verify {
            background: linear-gradient(45deg, #00f2ff, #0066ff);
            border: 1px solid rgba(255,255,255,0.2);
            box-shadow: 0 0 20px rgba(0, 102, 255, 0.3);
            transition: 0.3s;
        }
        .btn-verify:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 0 30px rgba(0, 242, 255, 0.6);
        }
        .btn-verify:active:not(:disabled) {
            transform: translateY(0);
        }
        .btn-verify:disabled {
            background: #333;
            cursor: not-allowed;
            box-shadow: none;
            opacity: 0.7;
        }

        /* أيقونة القفل */
        .lock-icon {
            background: rgba(0, 242, 255, 0.1);
            border: 1px solid rgba(0, 242, 255, 0.3);
            box-shadow: 0 0 20px rgba(0, 242, 255, 0.2);
        }
    </style>
</head>
<body class="flex items-center justify-center min-h-screen p-4">

    <div class="glass-card w-full max-w-sm p-10 rounded-[2.5rem] text-center">
        
        <!-- أيقونة القفل المتوهجة -->
        <div class="w-16 h-16 mx-auto rounded-full lock-icon flex items-center justify-center mb-8">
            <svg class="w-8 h-8 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path></svg>
        </div>

        <h3 class="text-cyan-400 font-bold mb-2 uppercase tracking-widest text-xs">Security Check</h3>
        <h2 class="text-2xl font-black mb-6 text-white uppercase">Verify Identity</h2>
        <p class="text-gray-400 text-xs mb-8">Enter the 4-digit code sent to your device</p>

        <!-- حقل الكود -->
        <input id="code" type="text" maxlength="4" placeholder="0000" 
            class="pin-input w-full p-4 rounded-2xl text-center text-5xl font-black outline-none mb-8"
            onfocus="this.select()" autocomplete="off">

        <!-- زر التحقق -->
        <button id="btn" onclick="check()" class="btn-verify w-full py-4 rounded-2xl font-black text-lg uppercase tracking-widest text-white">
            VERIFY 🛡️
        </button>
    </div>

    <script>
        // التركيز التلقائي على حقل الإدخال عند التحميل
        window.onload = function() {
            document.getElementById('code').focus();
        };

        // السماح بالضغط على Enter للإرسال
        document.getElementById('code').addEventListener('keypress', function (e) {
            if (e.key === 'Enter') {
                check();
            }
        });

        async function check() {
            const input = document.getElementById('code');
            const c = input.value;
            const btn = document.getElementById('btn');

            // تحقق بسيط من أن الكود مكون من 4 خانات
            if(c.length < 4) {
                input.style.borderColor = "red";
                setTimeout(() => input.style.borderColor = "rgba(255,255,255,0.1)", 1000);
                return;
            }

            // حالة التحميل
            btn.innerText = "VERIFYING...";
            btn.disabled = true;
            input.disabled = true;

            try {
                const res = await fetch('/api/verify_code', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({code: c})
                });
                const data = await res.json();
                
                if(res.ok) {
                    window.location.href = data.url;
                } else {
                    alert(data.message || "Invalid Code");
                    // إعادة الزر لحالته الطبيعية
                    btn.innerText = "VERIFY 🛡️";
                    btn.disabled = false;
                    input.disabled = false;
                    input.focus();
                    input.value = ""; // مسح الكود الخاطئ
                }
            } catch(e) {
                alert("Connection Error! Please try again.");
                btn.innerText = "VERIFY 🛡️";
                btn.disabled = false;
                input.disabled = false;
                input.focus();
            }
        }
    </script>
</body>
</html>
