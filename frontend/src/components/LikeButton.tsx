// COMPONENT: LikeButton
//
// This is a "controlled component" — it holds NO state of its own.
// The parent owns the truth (liked, likeCount) and passes them as props.
// When clicked, it calls onToggle() to tell the parent "the user clicked this".
// The parent then updates its state, which flows back down as new props.
//
// Pattern: data flows DOWN (props), events flow UP (callbacks)
//
// Props interface — describes exactly what this component needs:
interface Props {
  liked: boolean       // is this article currently liked by the user?
  likeCount: number   // total likes to display
  loading: boolean    // true while the API call is in-flight — disables the button
  onToggle: () => void  // function to call when the button is clicked
}

function LikeButton({ liked, likeCount, loading, onToggle }: Props) {
  return (
    <button
      // Swap between filled (liked) and outline (not liked) Bootstrap button styles
      className={`btn btn-sm ${liked ? 'btn-danger' : 'btn-outline-danger'}`}
      onClick={onToggle}
      disabled={loading}  // prevent double-clicks while waiting for API
    >
      {/* Ternary: if liked show filled heart, else show empty heart */}
      {liked ? '♥' : '♡'} {likeCount}
    </button>
  )
}

export default LikeButton
