import { Card, Typography, Spin, Empty, List, Tag } from 'antd';
import { useEffect, useState } from 'react';
import { Teacher, TeacherEvaluation } from '@/lib/models';

const { Text, Paragraph } = Typography;

interface CourseTeacherEvaluationsProps {
  teacher: Teacher;
  loading?: boolean;
}

const CourseTeacherEvaluations: React.FC<CourseTeacherEvaluationsProps> = ({
  teacher,
  loading = false,
}) => {
  const [evaluations, setEvaluations] = useState<TeacherEvaluation[]>([]);
  const [evaluationLoading, setEvaluationLoading] = useState(false);

  useEffect(() => {
    if (teacher?.id) {
      fetchTeacherEvaluations();
    }
  }, [teacher?.id]);

  const fetchTeacherEvaluations = async () => {
    setEvaluationLoading(true);
    try {
      const response = await fetch(`/api/teacher/${teacher.id}/evaluations`);
      if (response.ok) {
        const data = await response.json();
        setEvaluations(data.evaluations || []);
      }
    } catch (error) {
      console.error('获取教师评价失败:', error);
    } finally {
      setEvaluationLoading(false);
    }
  };

  const renderEvaluationItem = (evaluation: TeacherEvaluation) => (
    <List.Item key={evaluation.id}>
      <div style={{ width: '100%' }}>
        <Paragraph style={{ marginBottom: 8 }}>
          <Text>{evaluation.evaluation_content}</Text>
        </Paragraph>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Tag color="blue" style={{ fontSize: '12px' }}>
            {evaluation.data_sources}
          </Tag>
          <Text type="secondary" style={{ fontSize: '12px' }}>
            {new Date(evaluation.created_at).toLocaleDateString()}
          </Text>
        </div>
      </div>
    </List.Item>
  );

  if (loading || evaluationLoading) {
    return (
      <Card title={`教师评价`} style={{ marginBottom: 16 }}>
        <Spin size="large" style={{ display: 'block', textAlign: 'center', padding: '40px 0' }} />
      </Card>
    );
  }

  return (
    <Card 
      title={`${teacher?.name || '教师'}评价（${evaluations.length}条）`}
      style={{ marginBottom: 16 }}
    >
      {evaluations.length === 0 ? (
        <Empty
          description="暂无教师评价"
          image={Empty.PRESENTED_IMAGE_SIMPLE}
          style={{ padding: '20px 0' }}
        />
      ) : (
        <List
          dataSource={evaluations.slice(0, 10)} // 只显示前10条评价
          renderItem={renderEvaluationItem}
          size="small"
        />
      )}
      {evaluations.length > 10 && (
        <Text type="secondary" style={{ fontSize: '12px', marginTop: 8, display: 'block' }}>
          显示前10条评价，共{evaluations.length}条
        </Text>
      )}
    </Card>
  );
};

export default CourseTeacherEvaluations;
