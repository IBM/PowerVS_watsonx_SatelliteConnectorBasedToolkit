
import DataTable from './DataTable';
import PropTypes from 'prop-types'

const Message = ({ text, sender, type, data }) => {
  console.info('We are here ', text, sender, type, data);
  return (
    <div className={`message ${sender}`}>
      {type === 'table' ? (
                  <DataTable data={data} />
                ) : (
                  <p>{text}</p>
                )}
    </div>
  );
};

Message.propTypes = {
  text: PropTypes.string.isRequired,
  sender: PropTypes.string.isRequired,
  type: PropTypes.string.isRequired,
  data: PropTypes.object.isRequired,
}

export default Message;
