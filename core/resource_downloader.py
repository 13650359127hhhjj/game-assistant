#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
资源下载模块

本模块实现游戏资源的搜索和下载功能，
支持多种资源类型的检索和管理。
"""

import time
import random
from typing import List, Dict, Optional
from dataclasses import dataclass
from utils.logger import get_logger


@dataclass
class Resource:
    """资源数据类"""
    id: str
    name: str
    type: str
    size: str
    source: str
    url: str
    description: str = ""
    download_count: int = 0
    rating: float = 0.0


class ResourceDownloader:
    """游戏资源下载器类"""
    
    def __init__(self):
        """初始化资源下载器"""
        self.logger = get_logger(__name__)
        self._init_resource_database()
        self.download_history = []
        self.logger.info("资源下载器初始化完成")
    
    def _init_resource_database(self):
        """初始化资源数据库（模拟数据）"""
        # 模拟资源数据库
        self.resource_db = [
            # 补丁类资源
            Resource(
                id="PATCH_001",
                name="游戏优化补丁 v2.5",
                type="补丁",
                size="45.2 MB",
                source="官方更新",
                url="https://example.com/patch/v2.5",
                description="修复已知问题，提升游戏性能",
                download_count=15420,
                rating=4.8
            ),
            Resource(
                id="PATCH_002",
                name="汉化补丁 v1.2",
                type="补丁",
                size="12.8 MB",
                source="社区汉化组",
                url="https://example.com/patch/chinese",
                description="完整汉化，支持最新版本",
                download_count=8930,
                rating=4.5
            ),
            Resource(
                id="PATCH_003",
                name="修复补丁 v1.0.8",
                type="补丁",
                size="8.5 MB",
                source="官方更新",
                url="https://example.com/patch/fix",
                description="修复崩溃和内存泄漏问题",
                download_count=12100,
                rating=4.7
            ),
            
            # MOD类资源
            Resource(
                id="MOD_001",
                name="高清材质包 v3.0",
                type="MOD",
                size="2.1 GB",
                source="MOD社区",
                url="https://example.com/mod/texture",
                description="4K高清材质，提升画面表现",
                download_count=5620,
                rating=4.9
            ),
            Resource(
                id="MOD_002",
                name="角色美化MOD",
                type="MOD",
                size="156 MB",
                source="玩家自制",
                url="https://example.com/mod/beauty",
                description="美化主角外观，多种风格可选",
                download_count=9850,
                rating=4.3
            ),
            Resource(
                id="MOD_003",
                name="武器扩展包",
                type="MOD",
                size="320 MB",
                source="MOD社区",
                url="https://example.com/mod/weapon",
                description="新增20种特色武器",
                download_count=7340,
                rating=4.6
            ),
            Resource(
                id="MOD_004",
                name="画质增强MOD",
                type="MOD",
                size="890 MB",
                source="玩家自制",
                url="https://example.com/mod/graphics",
                description="支持光追效果，提升画质",
                download_count=4210,
                rating=4.7
            ),
            
            # 地图类资源
            Resource(
                id="MAP_001",
                name="新关卡地图包",
                type="地图",
                size="450 MB",
                source="官方DLC",
                url="https://example.com/map/newlevel",
                description="包含5个新关卡和隐藏地图",
                download_count=6780,
                rating=4.4
            ),
            Resource(
                id="MAP_002",
                name="多人竞技地图",
                type="地图",
                size="280 MB",
                source="社区创作",
                url="https://example.com/map/multiplayer",
                description="8张多人对战地图",
                download_count=8920,
                rating=4.5
            ),
            Resource(
                id="MAP_003",
                name="生存模式地图",
                type="地图",
                size="520 MB",
                source="玩家自制",
                url="https://example.com/map/survival",
                description="超大生存地图，支持多人合作",
                download_count=5430,
                rating=4.6
            ),
            
            # 皮肤类资源
            Resource(
                id="SKIN_001",
                name="角色服装包",
                type="皮肤",
                size="180 MB",
                source="玩家自制",
                url="https://example.com/skin/clothing",
                description="30套精美服装",
                download_count=11200,
                rating=4.2
            ),
            Resource(
                id="SKIN_002",
                name="武器皮肤合集",
                type="皮肤",
                size="95 MB",
                source="社区创作",
                url="https://example.com/skin/weapon",
                description="50款炫酷武器皮肤",
                download_count=9340,
                rating=4.4
            ),
            Resource(
                id="SKIN_003",
                name="UI主题包",
                type="皮肤",
                size="25 MB",
                source="玩家自制",
                url="https://example.com/skin/ui",
                description="多种界面主题风格",
                download_count=7650,
                rating=4.1
            ),
            
            # 音效类资源
            Resource(
                id="AUDIO_001",
                name="原声音乐包",
                type="音效",
                size="350 MB",
                source="官方发布",
                url="https://example.com/audio/ost",
                description="完整原声OST，包含所有背景音乐",
                download_count=4560,
                rating=4.8
            ),
            Resource(
                id="AUDIO_002",
                name="音效增强包",
                type="音效",
                size="120 MB",
                source="社区创作",
                url="https://example.com/audio/sfx",
                description="增强游戏音效，体验更佳",
                download_count=6780,
                rating=4.3
            ),
            Resource(
                id="AUDIO_003",
                name="语音包",
                type="音效",
                size="210 MB",
                source="玩家自制",
                url="https://example.com/audio/voice",
                description="多种语音风格选择",
                download_count=5430,
                rating=4.5
            )
        ]
        
        self.logger.info(f"已加载 {len(self.resource_db)} 个资源")
    
    def search(self, keyword: str, resource_type: Optional[str] = None) -> List[Dict]:
        """
        搜索资源
        
        Args:
            keyword: 搜索关键词
            resource_type: 资源类型过滤（可选）
            
        Returns:
            符合条件的资源列表
        """
        self.logger.info(f"开始搜索: keyword={keyword}, type={resource_type}")
        
        # 模拟搜索延迟
        time.sleep(0.3)
        
        results = []
        keyword_lower = keyword.lower()
        
        for resource in self.resource_db:
            # 检查关键词匹配
            if (keyword_lower in resource.name.lower() or 
                keyword_lower in resource.description.lower()):
                
                # 检查类型过滤
                if resource_type is None or resource_type == resource.type:
                    results.append({
                        'id': resource.id,
                        'name': resource.name,
                        'type': resource.type,
                        'size': resource.size,
                        'source': resource.source,
                        'url': resource.url,
                        'description': resource.description,
                        'download_count': resource.download_count,
                        'rating': resource.rating
                    })
        
        # 模拟没有精确匹配时返回部分匹配结果
        if not results and len(keyword) >= 2:
            # 返回所有资源作为备选
            for resource in self.resource_db[:5]:
                results.append({
                    'id': resource.id,
                    'name': resource.name,
                    'type': resource.type,
                    'size': resource.size,
                    'source': resource.source,
                    'url': resource.url,
                    'description': resource.description,
                    'download_count': resource.download_count,
                    'rating': resource.rating
                })
        
        # 按下载量排序
        results.sort(key=lambda x: x['download_count'], reverse=True)
        
        self.logger.info(f"搜索完成，找到 {len(results)} 个结果")
        return results
    
    def download(self, resource_id: str, save_path: str) -> bool:
        """
        下载资源
        
        Args:
            resource_id: 资源ID
            save_path: 保存路径
            
        Returns:
            是否下载成功
        """
        self.logger.info(f"开始下载资源: {resource_id}, 保存路径: {save_path}")
        
        # 查找资源
        resource = None
        for r in self.resource_db:
            if r.id == resource_id:
                resource = r
                break
        
        if not resource:
            self.logger.error(f"资源不存在: {resource_id}")
            return False
        
        # 模拟下载过程
        try:
            # 模拟下载进度
            for i in range(1, 11):
                time.sleep(0.2)
                self.logger.debug(f"下载进度: {i*10}%")
            
            # 记录下载历史
            self.download_history.append({
                'resource_id': resource_id,
                'resource_name': resource.name,
                'save_path': save_path,
                'download_time': time.strftime("%Y-%m-%d %H:%M:%S")
            })
            
            self.logger.info(f"资源下载完成: {resource.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"下载失败: {str(e)}")
            return False
    
    def get_resource_info(self, resource_id: str) -> Optional[Dict]:
        """
        获取资源详细信息
        
        Args:
            resource_id: 资源ID
            
        Returns:
            资源信息字典，不存在则返回None
        """
        for resource in self.resource_db:
            if resource.id == resource_id:
                return {
                    'id': resource.id,
                    'name': resource.name,
                    'type': resource.type,
                    'size': resource.size,
                    'source': resource.source,
                    'url': resource.url,
                    'description': resource.description,
                    'download_count': resource.download_count,
                    'rating': resource.rating
                }
        return None
    
    def get_download_history(self) -> List[Dict]:
        """
        获取下载历史
        
        Returns:
            下载历史列表
        """
        return self.download_history
    
    def clear_download_history(self):
        """清空下载历史"""
        self.download_history.clear()
        self.logger.info("下载历史已清空")
    
    def get_statistics(self) -> Dict:
        """
        获取统计信息
        
        Returns:
            统计信息字典
        """
        return {
            'total_resources': len(self.resource_db),
            'total_downloads': sum(r.download_count for r in self.resource_db),
            'download_history_count': len(self.download_history),
            'resource_types': list(set(r.type for r in self.resource_db)),
            'average_rating': sum(r.rating for r in self.resource_db) / len(self.resource_db)
        }
    
    def get_recommendations(self, count: int = 5) -> List[Dict]:
        """
        获取推荐资源
        
        Args:
            count: 推荐数量
            
        Returns:
            推荐资源列表
        """
        # 按评分和下载量综合排序
        sorted_resources = sorted(
            self.resource_db,
            key=lambda x: (x.rating * 0.4 + min(x.download_count / 10000, 1) * 0.6),
            reverse=True
        )
        
        return [
            {
                'id': r.id,
                'name': r.name,
                'type': r.type,
                'size': r.size,
                'source': r.source,
                'rating': r.rating,
                'download_count': r.download_count
            }
            for r in sorted_resources[:count]
        ]
