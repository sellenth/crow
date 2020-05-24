import React from 'react';
import LoadingIcon from './components/LoadingIcon';

const divStyle = {
  height: '100%',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
};

export default function Loading() {
  return (
    <div style={divStyle}>
      <LoadingIcon width="50vh" height="50vh" />
    </div>
  );
}
