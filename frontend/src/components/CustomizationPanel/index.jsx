import React, { useState } from 'react';
import ModelPreview from './Preview/ModelPreview';

/**
 * 数字人形象定制面板
 * 支持图片上传、模板选择，联动后端API
 */
const CustomizationPanel = () => {
  const [image, setImage] = useState(null);
  const [previewUrl, setPreviewUrl] = useState('');
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState(null);

  // 选择图片
  const handleImageChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setImage(e.target.files[0]);
    }
  };

  // 上传图片并请求后端生成模型
  const handleUpload = async () => {
    if (!image) return;
    setUploading(true);
    const formData = new FormData();
    formData.append('image', image);
    try {
      const res = await fetch('/api/appearance/upload', {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      setResult(data.data);
      setPreviewUrl(data.data.preview_url);
    } catch (err) {
      alert('上传失败，请重试');
    }
    setUploading(false);
  };

  return (
    <div className="customization-panel">
      <h2>数字人形象定制</h2>
      <input type="file" accept="image/png,image/jpeg" onChange={handleImageChange} />
      <button onClick={handleUpload} disabled={uploading || !image}>
        {uploading ? '上传中...' : '上传图片并生成模型'}
      </button>
      {previewUrl && <ModelPreview src={previewUrl} />}
      {result && <pre>{JSON.stringify(result, null, 2)}</pre>}
    </div>
  );
};

export default CustomizationPanel;
