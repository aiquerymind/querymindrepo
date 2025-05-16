import type { Message } from 'ai';
import React, { type RefCallback } from 'react';
import { ClientOnly } from 'remix-utils/client-only';
import { Menu } from '~/components/sidebar/Menu.client';
import { IconButton } from '~/components/ui/IconButton';
import { Workbench } from '~/components/workbench/Workbench.client';
import { classNames } from '~/utils/classNames';
import { Messages } from './Messages.client';
import { SendButton } from './SendButton.client';

const TEXTAREA_MIN_HEIGHT = 76;

const styles: { [key: string]: React.CSSProperties } = {
  container: {
    padding: '20px',
    textAlign: 'center',
    minHeight: '100vh',
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'center',
    backgroundImage: 'url("/homepage.jpg")',
    backgroundSize: 'cover',
    backgroundPosition: 'center',
    backgroundRepeat: 'no-repeat',
  },
  heading: {
    fontSize: 'clamp(32px, 5vw, 48px)',
    fontWeight: 700,
    background: 'linear-gradient(90deg, #1488FC, #A06D00)',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
    marginBottom: '10px',
    letterSpacing: '0.5px',
  },
  subheading: {
    fontSize: 'clamp(14px, 2vw, 16px)',
    background: 'linear-gradient(90deg, #1488FC, #A06D00)',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
    marginBottom: '30px',
    fontWeight: 400,
  },
  promptContainer: {
    position: 'relative',
    boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
    border: '1px solid #333',
    backgroundColor: 'rgba(26, 26, 26, 0.9)',
    backdropFilter: 'blur(4px)',
    borderRadius: '8px',
    marginBottom: '50px',
    width: 'clamp(300px, 80vw, 600px)',
    margin: '0 auto',
  },
  promptSvg: {
    position: 'absolute',
    top: 0,
    left: 0,
    width: '100%',
    height: '100%',
    pointerEvents: 'none',
  },
  promptEffectLine: {
    width: '100%',
    height: '100%',
    fill: 'none',
    stroke: 'url(#line-gradient)',
    strokeWidth: 2,
  },
  promptShine: {
    fill: 'url(#shine-gradient)',
  },
  promptInner: {
    position: 'relative',
    userSelect: 'none',
  },
  textarea: {
    width: '100%',
    padding: '16px 64px 16px 16px',
    outline: 'none',
    resize: 'none',
    background: 'transparent',
    color: '#A3A3A4',
    fontSize: 'clamp(12px, 1.5vw, 14px)',
    minHeight: '76px',
    maxHeight: '200px',
    height: '76px',
    overflowY: 'hidden',
    border: 'none',
  },
  promptActions: {
    display: 'flex',
    justifyContent: 'space-between',
    padding: '8px 16px',
  },
  actionLeft: {
    display: 'flex',
    gap: '4px',
    alignItems: 'center',
  },
  options: {
    display: 'flex',
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    gap: '20px',
    marginTop: '50px',
  },
  stackText: {
    fontSize: 'clamp(12px, 1.5vw, 14px)',
    color: '#737373',
    marginTop: '35px',
    fontWeight: 400,
  },
  stackIcons: {
    display: 'flex',
    justifyContent: 'center',
    gap: 'clamp(10px, 2vw, 15px)',
    flexWrap: 'wrap',
    marginTop: '35px',
  },
  icon: {
    fontSize: 'clamp(12px, 1.5vw, 14px)',
    color: '#737373',
    backgroundColor: 'rgba(51, 51, 51, 0.8)',
    padding: '5px 10px',
    borderRadius: '15px',
  },
};

interface BaseChatProps {
  textareaRef?: React.RefObject<HTMLTextAreaElement> | undefined;
  messageRef?: RefCallback<HTMLDivElement> | undefined;
  scrollRef?: RefCallback<HTMLDivElement> | undefined;
  showChat?: boolean;
  chatStarted?: boolean;
  isStreaming?: boolean;
  messages?: Message[];
  enhancingPrompt?: boolean;
  promptEnhanced?: boolean;
  input?: string;
  handleStop?: () => void;
  sendMessage?: (event: React.UIEvent, messageInput?: string) => void;
  handleInputChange?: (event: React.ChangeEvent<HTMLTextAreaElement>) => void;
  enhancePrompt?: () => void;
}

export const BaseChat = React.forwardRef<HTMLDivElement, BaseChatProps>(
  (
    {
      textareaRef,
      messageRef,
      scrollRef,
      showChat = true,
      chatStarted = false,
      isStreaming = false,
      enhancingPrompt = false,
      promptEnhanced = false,
      messages,
      input = '',
      sendMessage,
      handleInputChange,
      enhancePrompt,
      handleStop,
    },
    ref,
  ) => {
    const TEXTAREA_MAX_HEIGHT = chatStarted ? 400 : 200;

    return (
      <div
        ref={ref}
        style={styles.container}
        data-chat-visible={showChat}
      >
        <ClientOnly>{() => <Menu />}</ClientOnly>
        <div ref={scrollRef} style={{ flex: 1, overflowY: 'auto', width: '100%' }}>
          {!chatStarted && (
            <div id="intro" style={{ marginTop: '26vh', maxWidth: '600px', margin: '0 auto' }}>
              <h1 style={styles.heading}>WHAT DO YOU WANT TO CODE?</h1>
              <p style={styles.subheading}>
                Prompt, run, and edit Python scripts for data science with QueryMind AI.
              </p>
            </div>
          )}
          <div
            style={{
              padding: '24px',
              display: 'flex',
              flexDirection: 'column',
              height: chatStarted ? '100%' : 'auto',
            }}
          >
            <ClientOnly>
              {() =>
                chatStarted ? (
                  <Messages
                    ref={messageRef}
                    messages={messages}
                    isStreaming={isStreaming}
                    className="flex flex-col w-full flex-1 max-w-[600px] px-4 pb-6 mx-auto z-1"
                  />
                ) : null
              }
            </ClientOnly>
            <div
              style={{
                position: chatStarted ? 'sticky' : 'relative',
                bottom: 0,
                width: '100%',
                maxWidth: '600px',
                margin: '0 auto',
                zIndex: 10,
              }}
            >
              <div style={styles.promptContainer}>
                <svg style={styles.promptSvg}>
                  <defs>
                    <linearGradient
                      id="line-gradient"
                      x1="20%"
                      y1="0%"
                      x2="-14%"
                      y2="10%"
                      gradientUnits="userSpaceOnUse"
                      gradientTransform="rotate(-45)"
                    >
                      <stop offset="0%" stopColor="#1488FC" stopOpacity="0%" />
                      <stop offset="40%" stopColor="#1488FC" stopOpacity="80%" />
                      <stop offset="50%" stopColor="#1488FC" stopOpacity="80%" />
                      <stop offset="100%" stopColor="#1488FC" stopOpacity="0%" />
                    </linearGradient>
                  </defs>
                  <rect style={styles.promptEffectLine} pathLength="100" strokeLinecap="round" />
                  <rect style={styles.promptShine} x="48" y="24" width="70" height="1" />
                </svg>
                <div style={styles.promptInner}>
                  <textarea
                    ref={textareaRef}
                    style={{
                      ...styles.textarea,
                      minHeight: TEXTAREA_MIN_HEIGHT,
                      maxHeight: TEXTAREA_MAX_HEIGHT,
                    }}
                    placeholder="How can QueryMind help you today?"
                    value={input}
                    onChange={handleInputChange}
                    onKeyDown={(event) => {
                      if (event.key === 'Enter' && !event.shiftKey) {
                        event.preventDefault();
                        sendMessage?.(event);
                      }
                    }}
                    translate="no"
                  />
                </div>
                <div style={styles.promptActions}>
                  <div style={styles.actionLeft}>
                    <IconButton
                      title="Enhance prompt"
                      disabled={input.length === 0 || enhancingPrompt}
                      onClick={() => enhancePrompt?.()}
                    >
                      {enhancingPrompt ? (
                        <>
                          <div className="i-svg-spinners:90-ring-with-bg text-bolt-elements-loader-progress text-xl"></div>
                          <div style={{ marginLeft: '6px' }}>Enhancing prompt...</div>
                        </>
                      ) : (
                        <>
                          <div className="i-bolt:stars text-xl"></div>
                          {promptEnhanced && <div style={{ marginLeft: '6px' }}>Prompt enhanced</div>}
                        </>
                      )}
                    </IconButton>
                    <ClientOnly>
                      {() => (
                        <SendButton
                          show={input.length > 0 || isStreaming}
                          isStreaming={isStreaming}
                          onClick={(event) => {
                            if (isStreaming) {
                              handleStop?.();
                              return;
                            }
                            sendMessage?.(event);
                          }}
                        />
                      )}
                    </ClientOnly>
                  </div>
                  {input.length > 3 && (
                    <div style={{ fontSize: '12px', color: '#737373' }}>
                      Use <kbd style={{ padding: '2px 4px', background: '#333', borderRadius: '4px' }}>Shift</kbd> +{' '}
                      <kbd style={{ padding: '2px 4px', background: '#333', borderRadius: '4px' }}>Return</kbd> for a new line
                    </div>
                  )}
                </div>
              </div>
            </div>
            {!chatStarted && (
              <div id="examples" style={{ maxWidth: '600px', margin: '32px auto 0' }}>
                <div style={styles.options}>
                  <button className="option-btn">Load a CSV and visualize data with Matplotlib</button>
                  <button className="option-btn">Train a machine learning model with scikit-learn</button>
                  <button className="option-btn">Perform data cleaning with pandas</button>
                </div>
                <p style={styles.stackText}>or start with a popular data science library</p>
                <div style={styles.stackIcons}>
                  {['pandas', 'Matplotlib', 'scikit-learn', 'NumPy', 'BeautifulSoup', 'Airflow'].map((lib, index) => (
                    <span key={index} style={styles.icon}>{lib}</span>
                  ))}
                </div>
              </div>
            )}
          </div>
          <ClientOnly>{() => <Workbench chatStarted={chatStarted} isStreaming={isStreaming} />}</ClientOnly>
        </div>
      </div>
    );
  },
);