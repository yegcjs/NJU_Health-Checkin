# NJU_Health-Checkin

**使用方法**

1. 在config.json中填写南大统一身份认证的学号和密码以及上次核酸时间
2. 确保依赖库安装完整，`pip install -r requirements.txt`
3. `python checkin.py`后台运行即可运行一次
4. 若要每天自动运行，请在`contab -e`中添加以下命令：
	`0 12 * * * cd /path/to/checkin && python checkin.py`
5. 或自行查找如何设置Windows下的定时任务

:rotating_light:**请务必如实上报健康状况**，如有异地出行、身体状况变动、本人或家人健康码非绿色，请停止使用此脚本。

### 参考&感谢

[yp51md/NJUcheckin](https://github.com/yp51md/NJUcheckin)  
[Boris-code/feapder](https://github.com/Boris-code/feapder)