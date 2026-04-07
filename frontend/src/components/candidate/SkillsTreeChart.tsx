import { useEffect, useRef } from 'react';
import * as echarts from 'echarts';

interface Skill {
  id?: string;
  skill_name: string;
  category?: string;
  proficiency_level?: string;
  confidence_score?: number;
  years_experience?: number;
}

interface SkillsTreeChartProps {
  skills: (string | Skill)[];
}

export default function SkillsTreeChart({ skills }: SkillsTreeChartProps) {
  const chartRef = useRef<HTMLDivElement>(null);
  const chartInstance = useRef<echarts.ECharts | null>(null);

  useEffect(() => {
    if (!chartRef.current || !skills || skills.length === 0) return;

    // Initialize chart
    if (!chartInstance.current) {
      chartInstance.current = echarts.init(chartRef.current);
    }

    // Group skills by category dynamically from data
    const groupSkillsByCategory = () => {
      const categories: { [key: string]: Skill[] } = {};

      skills.forEach(skill => {
        // Handle both string and object formats
        let skillObj: Skill;
        if (typeof skill === 'string') {
          skillObj = { skill_name: skill, category: 'Other' };
        } else {
          skillObj = skill;
        }

        const category = skillObj.category || 'Other';
        if (!categories[category]) {
          categories[category] = [];
        }
        categories[category].push(skillObj);
      });

      return categories;
    };

    const categories = groupSkillsByCategory();

    // Build tree data structure with proficiency levels and confidence
    const treeData = {
      name: 'Skills',
      children: Object.entries(categories)
        .filter(([_, skills]) => skills.length > 0)
        .map(([category, categorySkills]) => ({
          name: category,
          children: categorySkills.map(skill => {
            const level = skill.proficiency_level ? ` (${skill.proficiency_level})` : '';
            const confidence = skill.confidence_score !== undefined 
              ? ` - ${Math.round(skill.confidence_score * 100)}%` 
              : '';
            return {
              name: `${skill.skill_name}${level}${confidence}`,
              value: skill.confidence_score || 0.5,
              itemStyle: {
                color: skill.confidence_score 
                  ? (skill.confidence_score >= 0.8 ? '#10b981' : skill.confidence_score >= 0.5 ? '#f59e0b' : '#ef4444')
                  : '#6b7280'
              }
            };
          })
        }))
    };

    const option = {
      tooltip: {
        trigger: 'item',
        triggerOn: 'mousemove'
      },
      series: [
        {
          type: 'tree',
          data: [treeData],
          top: '10%',
          left: '10%',
          bottom: '10%',
          right: '20%',
          symbolSize: 7,
          label: {
            position: 'left',
            verticalAlign: 'middle',
            align: 'right',
            fontSize: 11
          },
          leaves: {
            label: {
              position: 'right',
              verticalAlign: 'middle',
              align: 'left'
            }
          },
          emphasis: {
            focus: 'descendant'
          },
          expandAndCollapse: true,
          animationDuration: 550,
          animationDurationUpdate: 750,
          initialTreeDepth: 2
        }
      ]
    };

    chartInstance.current.setOption(option);

    // Handle resize
    const handleResize = () => {
      chartInstance.current?.resize();
    };
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      if (chartInstance.current) {
        chartInstance.current.dispose();
        chartInstance.current = null;
      }
    };
  }, [skills]);

  if (!skills || skills.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-500">
        No skills data available
      </div>
    );
  }

  return (
    <div 
      ref={chartRef} 
      style={{ width: '100%', height: '500px' }}
      className="bg-white rounded-lg"
    />
  );
}
