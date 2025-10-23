import React, { useState } from 'react';

/**
 * 音色定制面板
 * 支持音频样本上传、音色选择，联动后端API
 */
const VoiceControls = () => {
  const [audio, setAudio] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState(null);

  // 选择音频文件
  const handleAudioChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setAudio(e.target.files[0]);
    }
  };

  // 上传音频样本并请求后端创建音色配置
  const handleUpload = async () => {
    if (!audio) return;
    setUploading(true);
    const formData = new FormData();
    formData.append('audio', audio);
    try {
      const res = await fetch('/api/voice/upload', {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      setResult(data.data);
    } catch (err) {
      alert('上传失败，请重试');
    }
    setUploading(false);
  };

  return (
    <div className="voice-controls">
      <h2>音色定制</h2>
      <input type="file" accept="audio/wav,audio/mpeg" onChange={handleAudioChange} />
      <button onClick={handleUpload} disabled={uploading || !audio}>
        {uploading ? '上传中...' : '上传音频样本'}
      </button>
      {result && (
        <div>
          <h3>音色配置结果</h3>
          <pre>{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
    </div>
  );
};

export default VoiceControls;
