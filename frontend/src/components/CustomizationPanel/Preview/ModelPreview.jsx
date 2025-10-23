import React from 'react';

/**
 * 3D数字人模型预览组件
 * 使用 model-viewer 或 Three.js 实现
 * @param {string} src - 3D模型文件URL
 */
const ModelPreview = ({ src }) => {
  if (!src) return null;
  return (
    <div className="model-preview">
      <h3>数字人3D模型预览</h3>
      {/* 推荐使用 <model-viewer>，如需更高定制可用 Three.js */}
      <model-viewer src={src} alt="数字人模型" auto-rotate camera-controls style={{ width: '400px', height: '400px' }} />
    </div>
  );
};

export default ModelPreview;
