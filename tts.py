"""
校园智能广播系统 - TTS语音模块
统一接口设计，支持Edge TTS（微软）和小米TTS
"""

import os
import hashlib
import asyncio
import logging
import json
import base64
from pathlib import Path

# TTS缓存目录（放在static下，Flask可直接访问）
TTS_CACHE_DIR = "static/tts_cache"

# Edge TTS中文音色列表
EDGE_VOICES = [
    {"id": "zh-CN-XiaoxiaoNeural", "name": "晓晓", "gender": "女", "style": "温暖亲切", "default": True},
    {"id": "zh-CN-YunxiNeural", "name": "云希", "gender": "男", "style": "阳光少年"},
    {"id": "zh-CN-YunjianNeural", "name": "云健", "gender": "男", "style": "沉稳大气"},
    {"id": "zh-CN-XiaoyiNeural", "name": "晓艺", "gender": "女", "style": "活泼可爱"},
    {"id": "zh-CN-YunyangNeural", "name": "云扬", "gender": "男", "style": "新闻播报"},
    {"id": "zh-CN-XiaochenNeural", "name": "晓辰", "gender": "女", "style": "专业成熟"},
    {"id": "zh-CN-XiaohanNeural", "name": "晓涵", "gender": "女", "style": "温柔体贴"},
    {"id": "zh-CN-XiaomengNeural", "name": "晓梦", "gender": "女", "style": "甜美可爱"},
    {"id": "zh-CN-XiaomoNeural", "name": "晓墨", "gender": "女", "style": "文艺清新"},
    {"id": "zh-CN-XiaoqiuNeural", "name": "晓秋", "gender": "女", "style": "成熟稳重"},
    {"id": "zh-CN-XiaoruiNeural", "name": "晓睿", "gender": "女", "style": "专业播报"},
    {"id": "zh-CN-XiaoshuangNeural", "name": "晓双", "gender": "女", "style": "童声"},
    {"id": "zh-CN-XiaoyanNeural", "name": "晓颜", "gender": "女", "style": "活力四射"},
    {"id": "zh-CN-XiaozhenNeural", "name": "晓甄", "gender": "女", "style": "端庄大方"},
]

# 小米TTS音色列表（9种音色，使用中文名）
XIAOMI_VOICES = [
    {"id": "冰糖", "name": "冰糖 (女) 清甜明亮", "gender": "女", "style": "清甜明亮，活泼可爱"},
    {"id": "茉莉", "name": "茉莉 (女) 温柔细腻", "gender": "女", "style": "温柔细腻，清新淡雅"},
    {"id": "Mia", "name": "Mia (女) 优雅知性", "gender": "女", "style": "优雅知性，温和亲切"},
    {"id": "Chloe", "name": "Chloe (女) 甜美温柔", "gender": "女", "style": "甜美温柔，情感丰富", "default": True},
    {"id": "苏打", "name": "苏打 (男) 清爽自然", "gender": "男", "style": "清爽自然，年轻活力"},
    {"id": "Milo", "name": "Milo (男) 温暖磁性", "gender": "男", "style": "温暖磁性，亲和力强"},
    {"id": "白桦", "name": "白桦 (男) 沉稳厚重", "gender": "男", "style": "沉稳厚重，专业权威"},
    {"id": "Dean", "name": "Dean (男) 浑厚低沉", "gender": "男", "style": "浑厚低沉，刚毅有力"},
]


def _get_logger():
    """获取logger（延迟获取，确保logging已配置）"""
    return logging.getLogger("SchoolBell")


class TTSProvider:
    """TTS统一接口基类"""
    
    def generate(self, text, output_path, voice=None, rate="+0%", volume="+0%"):
        raise NotImplementedError
    
    def list_voices(self):
        raise NotImplementedError


class EdgeTTSProvider(TTSProvider):
    """Edge TTS实现（微软）"""
    
    def generate(self, text, output_path, voice="zh-CN-XiaoxiaoNeural", rate="+0%", volume="+0%"):
        logger = _get_logger()
        try:
            import edge_tts
            
            output_dir = os.path.dirname(output_path)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
            
            logger.info(f"EdgeTTS生成: text={text[:30]}..., voice={voice}")
            
            asyncio.run(self._generate_async(text, output_path, voice, rate, volume))
            
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                logger.info(f"EdgeTTS生成成功: {output_path} ({os.path.getsize(output_path)} bytes)")
                return True
            else:
                logger.error(f"EdgeTTS生成失败: 文件为空或不存在")
                return False
                
        except ImportError:
            logger.error("edge-tts未安装，请运行: pip install edge-tts")
            return False
        except Exception as e:
            logger.error(f"EdgeTTS生成异常: {e}", exc_info=True)
            return False
    
    async def _generate_async(self, text, output_path, voice, rate, volume):
        import edge_tts
        communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate, volume=volume)
        await communicate.save(output_path)
    
    def list_voices(self):
        return EDGE_VOICES


class XiaoaiTTSProvider(TTSProvider):
    """小米TTS实现（MiMo-V2.5-TTS）"""
    
    SAMPLE_RATE = 24000
    CHANNELS = 1
    BITS_PER_SAMPLE = 16
    
    def _build_wav(self, pcm_data):
        """将PCM数据转换为WAV格式"""
        import struct
        data_length = len(pcm_data)
        header_length = 44
        buffer = bytearray(header_length + data_length)
        
        # RIFF头
        buffer[0:4] = b'RIFF'
        struct.pack_into('<I', buffer, 4, 36 + data_length)
        buffer[8:12] = b'WAVE'
        
        # fmt块
        buffer[12:16] = b'fmt '
        struct.pack_into('<I', buffer, 16, 16)  # 块大小
        struct.pack_into('<H', buffer, 20, 1)   # PCM格式
        struct.pack_into('<H', buffer, 22, self.CHANNELS)
        struct.pack_into('<I', buffer, 24, self.SAMPLE_RATE)
        struct.pack_into('<I', buffer, 28, self.SAMPLE_RATE * self.CHANNELS * (self.BITS_PER_SAMPLE // 8))
        struct.pack_into('<H', buffer, 32, self.CHANNELS * (self.BITS_PER_SAMPLE // 8))
        struct.pack_into('<H', buffer, 34, self.BITS_PER_SAMPLE)
        
        # data块
        buffer[36:40] = b'data'
        struct.pack_into('<I', buffer, 40, data_length)
        
        # 复制PCM数据
        buffer[44:] = pcm_data
        
        return bytes(buffer)
    
    def generate(self, text, output_path, voice="Chloe", rate="+0%", volume="+0%"):
        logger = _get_logger()
        try:
            from models import get_setting
            
            api_key = get_setting("xiaomi_api_key", "")
            if not api_key:
                logger.error("小米TTS API Key未配置")
                return False
            
            output_dir = os.path.dirname(output_path)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
            
            logger.info(f"小米TTS生成: text={text[:30]}..., voice={voice}")
            
            import urllib.request
            
            # 小米TTS格式：pcm16格式，中文音色名
            request_data = {
                "model": "mimo-v2.5-tts",
                "messages": [
                    {"role": "user", "content": "用清晰自然的声音朗读以下内容"},
                    {"role": "assistant", "content": text}
                ],
                "audio": {
                    "format": "pcm16",
                    "voice": voice
                }
            }
            
            req = urllib.request.Request(
                "https://api.xiaomimimo.com/v1/chat/completions",
                data=json.dumps(request_data).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}"
                }
            )
            
            resp = urllib.request.urlopen(req, timeout=30)
            result = json.loads(resp.read().decode("utf-8"))
            
            # 提取PCM数据并转换为WAV
            if "choices" in result and len(result["choices"]) > 0:
                message = result["choices"][0].get("message", {})
                audio_data = message.get("audio", {})
                if "data" in audio_data:
                    pcm_bytes = base64.b64decode(audio_data["data"])
                    wav_bytes = self._build_wav(pcm_bytes)
                    
                    with open(output_path, "wb") as f:
                        f.write(wav_bytes)
                    
                    if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                        logger.info(f"小米TTS生成成功: {output_path} ({os.path.getsize(output_path)} bytes)")
                        return True
            
            logger.error(f"小米TTS生成失败: 响应格式异常")
            return False
                
        except Exception as e:
            logger.error(f"小米TTS生成异常: {e}", exc_info=True)
            return False
    
    def list_voices(self):
        return XIAOMI_VOICES


class TTSManager:
    """TTS管理器 - 带缓存，支持多provider"""
    
    def __init__(self):
        self.providers = {
            "edge": EdgeTTSProvider(),
            "xiaomi": XiaoaiTTSProvider()
        }
        self._ensure_cache_dir()
    
    def _ensure_cache_dir(self):
        os.makedirs(TTS_CACHE_DIR, exist_ok=True)
    
    def _get_provider(self):
        """获取当前配置的provider"""
        from models import get_setting
        provider_name = get_setting("tts_provider", "edge")
        return self.providers.get(provider_name, self.providers["edge"])
    
    def _get_cache_path(self, text, voice, provider):
        content = f"{text}:{voice}:{provider}"
        filename = hashlib.md5(content.encode()).hexdigest() + ".mp3"
        return os.path.join(TTS_CACHE_DIR, filename)
    
    def generate(self, text, voice=None, rate="+0%", volume="+0%", use_cache=True):
        logger = _get_logger()
        
        if not text or not text.strip():
            logger.warning("TTS文本为空")
            return None
        
        if len(text) > 500:
            text = text[:500]
            logger.warning("TTS文本过长，已截断至500字")
        
        provider = self._get_provider()
        provider_name = "edge" if isinstance(provider, EdgeTTSProvider) else "xiaomi"
        
        if not voice:
            from models import get_setting
            if provider_name == "xiaomi":
                voice = get_setting("xiaomi_voice", "Chloe")
            else:
                voice = get_setting("tts_voice", "zh-CN-XiaoxiaoNeural")
        
        cache_path = self._get_cache_path(text, voice, provider_name)
        if use_cache and os.path.exists(cache_path) and os.path.getsize(cache_path) > 0:
            logger.debug(f"TTS命中缓存: {cache_path}")
            return cache_path
        
        success = provider.generate(text, cache_path, voice, rate, volume)
        if success:
            return cache_path
        return None
    
    def preview(self, text, voice=None):
        logger = _get_logger()
        logger.info(f"TTS.preview called: text={text[:50] if text else 'None'}, voice={voice}")
        
        if not text or not text.strip():
            return None
        
        if len(text) > 100:
            text = text[:100]
        
        provider = self._get_provider()
        provider_name = "edge" if isinstance(provider, EdgeTTSProvider) else "xiaomi"
        
        if not voice:
            from models import get_setting
            if provider_name == "xiaomi":
                voice = get_setting("xiaomi_voice", "Chloe")
            else:
                voice = get_setting("tts_voice", "zh-CN-XiaoxiaoNeural")
        
        import time
        preview_path = os.path.join(TTS_CACHE_DIR, f"preview_{int(time.time())}.mp3")
        
        try:
            success = provider.generate(text, preview_path, voice)
            if success:
                return preview_path
            return None
        except Exception as e:
            logger.error(f"TTS.preview 异常: {e}", exc_info=True)
            return None
    
    def list_voices(self):
        provider = self._get_provider()
        return provider.list_voices()
    
    def list_all_voices(self):
        """列出所有provider的音色"""
        result = {}
        for name, provider in self.providers.items():
            result[name] = provider.list_voices()
        return result
    
    def cleanup_cache(self, max_age_hours=24):
        import time
        logger = _get_logger()
        now = time.time()
        count = 0
        
        for f in Path(TTS_CACHE_DIR).glob("*.mp3"):
            if f.name.startswith("preview_"):
                age_hours = (now - f.stat().st_mtime) / 3600
                if age_hours > max_age_hours:
                    f.unlink()
                    count += 1
        
        if count:
            logger.info(f"TTS缓存清理: 删除 {count} 个过期预览文件")


# 全局TTS管理器实例
tts_manager = TTSManager()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("测试TTS模块...")
    print(f"Edge TTS音色: {len(EDGE_VOICES)}个")
    print(f"小米TTS音色: {len(XIAOMI_VOICES)}个")
