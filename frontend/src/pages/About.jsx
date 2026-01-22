import { Button, Result } from 'antd';

import useLanguage from '@/locale/useLanguage';

const About = () => {
  const translate = useLanguage();
  return (
    <Result
      status="info"
      title={'IDURAR'}
      extra={
        <>
          <p>
            GitHub :{' '}
            <a href="https://github.com/prajwal-221/Customer-Relationship-Management">
              https://github.com/prajwal-221/Customer-Relationship-Management
            </a>
          </p>
        </>
      }
    />
  );
};

export default About;
