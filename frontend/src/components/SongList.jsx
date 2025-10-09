export default function SongList({ songs }) {
  return (
    <ul>
      {songs.map((s) => (
        <li key={s.id}>{s.title}</li>
      ))}
    </ul>
  );
}
