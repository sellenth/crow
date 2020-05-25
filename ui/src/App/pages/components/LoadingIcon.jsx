/* eslint-disable no-await-in-loop */
import React from 'react';
import { animated } from 'react-spring';
import { Keyframes } from 'react-spring/renderprops';
import { ReactComponent as Logo } from '../assets/paths/crow_head.svg';

const background = {
  height: '99%',
  width: '99%',
  borderRadius: '50%',
  background: 'black',
};

const iconContainer = {
  position: 'relative',
  borderRadius: '50%',
  overflow: 'hidden',
  maxHeight: '80vw',
  maxWidth: '80vw',
};

const outline = {
  position: 'absolute',
  top: '0',
  left: '0',
  zIndex: '10',
  fill: 'none',
  strokeWidth: '10px',
  stroke: '#EEEEEE',
  width: '122%',
  height: '100%',
  strokeDasharray: '1650',
};

const Content = Keyframes.Spring(async (next) => {
  // None of this will cause React to render, the component renders only once :-)
  while (true) {
    await next({
      from: {
        strokeDashoffset: 0,
      },
      strokeDashoffset: 1100,
      config: {
        mass: 1, tension: 70, friction: 20, precision: 0.1,
      },
    });
    await next({
      from: {
        strokeDashoffset: 1100,
      },
      strokeDashoffset: 0,
      config: {
        mass: 1, tension: 50, friction: 20, precision: 0.1,
      },
    });
  }
});

export default function LoadingIcon(props) {
  return (
    <div style={{ ...props, ...iconContainer }}>
      <div style={background} />
      <Content>
        {(style) => (
          <animated.svg style={{ ...outline, ...style }}>
            <Logo />
          </animated.svg>

        )}
      </Content>
    </div>
  );
}
